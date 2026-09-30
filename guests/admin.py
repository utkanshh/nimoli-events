from django.contrib import admin

from .models import CrewMember, Event, Expense, Guest, GuestField


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "venue", "start_date", "end_date")
    search_fields = ("name", "venue")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "category", "amount", "spent_on")
    list_filter = ("event", "category")
    search_fields = ("title", "category")


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ("event", "name", "role", "phone", "email")
    list_filter = ("event", "role")
    search_fields = ("name", "role", "phone", "email")


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "rsvp_status",
        "hotel_status",
        "whatsapp_opt_in",
        "updated_at",
    )
    list_filter = ("rsvp_status", "hotel_status", "whatsapp_opt_in")
    search_fields = ("name", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(GuestField)
class GuestFieldAdmin(admin.ModelAdmin):
    list_display = ("label", "created_at")
    search_fields = ("label",)
