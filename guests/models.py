import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


def event_media_upload_path(instance, filename):
    extension = filename.rsplit(".", 1)[-1].lower()
    return f"event-media/{instance.event_id}/{uuid.uuid4().hex}.{extension}"


class Event(models.Model):
    name = models.CharField(max_length=150)
    venue = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "name"]

    def __str__(self):
        return self.name


class EventMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Photo"
        VIDEO = "video", "Video"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to=event_media_upload_path)
    title = models.CharField(max_length=100, blank=True)
    media_type = models.CharField(max_length=8, choices=MediaType.choices)
    content_type = models.CharField(max_length=32)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="uploaded_event_media",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title or f"{self.get_media_type_display()} for {self.event}"


@receiver(post_delete, sender=EventMedia)
def delete_event_media_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)


class Expense(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=80, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_on = models.DateField(blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-spent_on", "-created_at"]

    def __str__(self):
        return self.title


class CrewMember(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="crew")
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=100)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} · {self.role}"


class Guest(models.Model):
    class GuestType(models.TextChoices):
        OUTSTATION = "outstation", "Outstation"
        LOCAL_STAY = "local_stay", "Local Stay"
        LOCAL_NON_STAY = "local_non_stay", "Local Non-Stay"
        INTERNATIONAL = "international", "International"

    class SideTag(models.TextChoices):
        BRIDE = "bride", "Bride’s side"
        GROOM = "groom", "Groom’s side"

    class SubCategory(models.TextChoices):
        SINGLE = "single", "Single"
        COUPLE = "couple", "Couple"

    class RoomPreference(models.TextChoices):
        SINGLE = "single", "Single room"
        DOUBLE = "double", "Double room"
        TWIN = "twin", "Twin room"
        NONE = "none", "No room needed"

    class RSVPStatus(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        PENDING = "pending", "Awaiting reply"
        DECLINED = "declined", "Declined"

    class HotelStatus(models.TextChoices):
        NOT_SELECTED = "not_selected", "Not selected"
        ONE_NIGHT = "one_night", "Booked · 1 night"
        TWO_NIGHTS = "two_nights", "Booked · 2 nights"
        THREE_NIGHTS = "three_nights", "Booked · 3 nights"

    name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    group_serial = models.PositiveIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)
    country_code = models.CharField(max_length=6, blank=True)
    invited_date = models.DateField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    pax = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    guest_type = models.CharField(max_length=24, choices=GuestType.choices, blank=True)
    side_tag = models.CharField(max_length=8, choices=SideTag.choices, blank=True)
    sub_category = models.CharField(
        max_length=8, choices=SubCategory.choices, blank=True
    )
    invite_name = models.CharField(max_length=150, blank=True)
    salutation = models.CharField(max_length=40, blank=True)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="guests",
        blank=True,
        null=True,
    )
    rsvp_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    rsvp_status = models.CharField(
        max_length=16, choices=RSVPStatus.choices, default=RSVPStatus.PENDING
    )
    hotel_status = models.CharField(
        max_length=16,
        choices=HotelStatus.choices,
        default=HotelStatus.NOT_SELECTED,
    )
    whatsapp_opt_in = models.BooleanField(default=False)
    whatsapp_opt_in_at = models.DateTimeField(blank=True, null=True)
    whatsapp_opted_out_at = models.DateTimeField(blank=True, null=True)
    hotel_check_in = models.DateField(blank=True, null=True)
    hotel_check_out = models.DateField(blank=True, null=True)
    room_preference = models.CharField(
        max_length=8,
        choices=RoomPreference.choices,
        default=RoomPreference.NONE,
    )
    custom_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "name"]
    def __str__(self):
        return self.name


class WhatsAppCampaign(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Sending"
        COMPLETED = "completed", "Completed"
        COMPLETED_WITH_ERRORS = "completed_with_errors", "Completed with errors"
        FAILED = "failed", "Failed"

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="whatsapp_campaigns"
    )
    template_name = models.CharField(max_length=512)
    language_code = models.CharField(max_length=16, default="en")
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.QUEUED
    )
    recipient_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.template_name} · {self.event.name}"


class WhatsAppCampaignRecipient(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    campaign = models.ForeignKey(
        WhatsAppCampaign, on_delete=models.CASCADE, related_name="recipients"
    )
    guest = models.ForeignKey(
        Guest, on_delete=models.CASCADE, related_name="whatsapp_campaigns"
    )
    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.QUEUED
    )
    provider_message_id = models.CharField(max_length=128, blank=True)
    error_message = models.CharField(max_length=500, blank=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "guest"], name="unique_campaign_guest"
            )
        ]


class GuestField(models.Model):
    label = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return self.label
