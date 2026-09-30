import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from guests.models import WhatsAppCampaign, WhatsAppCampaignRecipient
from guests.views import guest_whatsapp_number


def send_template_message(campaign, recipient):
    guest = recipient.guest
    phone_number = guest_whatsapp_number(guest)
    if not phone_number:
        return "", "Guest phone number is not a valid international number."

    rsvp_url = (
        f"{settings.PUBLIC_BASE_URL}{reverse('guest_rsvp', args=[guest.rsvp_token])}"
    )
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": campaign.template_name,
            "language": {"code": campaign.language_code},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": guest.invite_name or guest.name or guest.last_name or "Guest",
                        },
                        {"type": "text", "text": rsvp_url},
                    ],
                }
            ],
        },
    }
    api_url = (
        f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/"
        f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    request = Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            response_data = json.loads(error.read().decode("utf-8"))
            provider_error = response_data.get("error", {})
            error_code = provider_error.get("code")
            error_type = provider_error.get("type", "WhatsApp API error")
            detail = f"{error_type} ({error_code})" if error_code else error_type
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            detail = f"WhatsApp API returned HTTP {error.code}."
        return "", detail[:500]
    except URLError as error:
        return "", f"Could not reach WhatsApp API: {error.reason}"[:500]
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "", "WhatsApp API returned an invalid response."

    if not isinstance(result, dict):
        return "", "WhatsApp API returned an invalid response."
    messages = result.get("messages", [])
    if not messages or not messages[0].get("id"):
        return "", "WhatsApp API response did not include a message ID."
    return str(messages[0]["id"])[:128], ""


class Command(BaseCommand):
    help = "Send queued opted-in WhatsApp Business template messages one-to-one."

    def add_arguments(self, parser):
        parser.add_argument(
            "--campaign-id",
            type=int,
            help="Send only this queued campaign.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show queued campaign counts without sending messages.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm that the reviewed queued campaign(s) should be sent.",
        )

    def handle(self, *args, **options):
        if not all(
            (
                settings.WHATSAPP_PHONE_NUMBER_ID,
                settings.WHATSAPP_ACCESS_TOKEN,
                settings.WHATSAPP_API_VERSION,
            )
        ):
            raise CommandError(
                "Configure WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, and "
                "WHATSAPP_API_VERSION before sending."
            )
        if not re.fullmatch(r"v\d+\.\d+", settings.WHATSAPP_API_VERSION):
            raise CommandError("WHATSAPP_API_VERSION must look like vXX.X.")
        if not re.fullmatch(r"\d+", settings.WHATSAPP_PHONE_NUMBER_ID):
            raise CommandError("WHATSAPP_PHONE_NUMBER_ID must contain digits only.")
        if not settings.PUBLIC_BASE_URL.startswith("https://"):
            raise CommandError("GATHER_PUBLIC_BASE_URL must be a public HTTPS URL.")

        queued_campaigns = WhatsAppCampaign.objects.filter(
            status=WhatsAppCampaign.Status.QUEUED
        )
        campaign_id = options["campaign_id"]
        if campaign_id is not None:
            queued_campaigns = queued_campaigns.filter(pk=campaign_id)
        campaign_ids = list(
            queued_campaigns.order_by("created_at").values_list("pk", flat=True)
        )
        if campaign_id is not None and not campaign_ids:
            raise CommandError(f"Queued campaign {campaign_id} was not found.")
        if options["dry_run"]:
            for campaign in queued_campaigns.order_by("created_at"):
                queued_recipients = campaign.recipients.filter(
                    status=WhatsAppCampaignRecipient.Status.QUEUED
                ).select_related("guest")
                eligible_count = sum(
                    recipient.guest.whatsapp_opt_in
                    and recipient.guest.whatsapp_opted_out_at is None
                    and guest_whatsapp_number(recipient.guest) is not None
                    for recipient in queued_recipients
                )
                queued_count = campaign.recipients.filter(
                    status=WhatsAppCampaignRecipient.Status.QUEUED
                ).count()
                self.stdout.write(
                    f"Campaign {campaign.pk}: {campaign.template_name} "
                    f"({campaign.language_code}), {eligible_count} currently opted-in "
                    f"eligible recipient(s), {queued_count - eligible_count} will be skipped. "
                    "No messages sent."
                )
            if not campaign_ids:
                self.stdout.write("No queued campaigns.")
            return
        if not options["confirm"]:
            raise CommandError(
                "No messages sent. Review queued campaigns with --dry-run, then "
                "specify --confirm and preferably --campaign-id."
            )

        for campaign_id in campaign_ids:
            with transaction.atomic():
                claimed = WhatsAppCampaign.objects.filter(
                    pk=campaign_id,
                    status=WhatsAppCampaign.Status.QUEUED,
                ).update(
                    status=WhatsAppCampaign.Status.RUNNING,
                    started_at=timezone.now(),
                )
            if not claimed:
                continue

            campaign = WhatsAppCampaign.objects.get(pk=campaign_id)
            for recipient in campaign.recipients.filter(
                status=WhatsAppCampaignRecipient.Status.QUEUED
            ).select_related("guest"):
                if not recipient.guest.whatsapp_opt_in or recipient.guest.whatsapp_opted_out_at:
                    message_id, error_message = "", "Guest is no longer opted in."
                else:
                    message_id, error_message = send_template_message(campaign, recipient)
                if error_message:
                    recipient.status = WhatsAppCampaignRecipient.Status.FAILED
                    recipient.error_message = error_message
                else:
                    recipient.status = WhatsAppCampaignRecipient.Status.SENT
                    recipient.provider_message_id = message_id
                    recipient.sent_at = timezone.now()
                    recipient.guest.invited_date = timezone.localdate()
                    recipient.guest.save(update_fields=["invited_date"])
                recipient.save(
                    update_fields=[
                        "status",
                        "error_message",
                        "provider_message_id",
                        "sent_at",
                    ]
                )
                if settings.WHATSAPP_SEND_INTERVAL:
                    time.sleep(settings.WHATSAPP_SEND_INTERVAL)

            campaign.sent_count = campaign.recipients.filter(
                status=WhatsAppCampaignRecipient.Status.SENT
            ).count()
            campaign.failed_count = campaign.recipients.filter(
                status=WhatsAppCampaignRecipient.Status.FAILED
            ).count()
            campaign.status = (
                WhatsAppCampaign.Status.COMPLETED_WITH_ERRORS
                if campaign.failed_count
                else WhatsAppCampaign.Status.COMPLETED
            )
            campaign.finished_at = timezone.now()
            campaign.save(
                update_fields=[
                    "sent_count",
                    "failed_count",
                    "status",
                    "finished_at",
                ]
            )
            self.stdout.write(
                f"Campaign {campaign.pk}: {campaign.sent_count} sent, "
                f"{campaign.failed_count} failed."
            )
