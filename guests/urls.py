from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("events/", views.event_list, name="event_list"),
    path("events/<int:event_id>/select/", views.select_event, name="select_event"),
    path("events/media/upload/", views.upload_event_media, name="upload_event_media"),
    path("events/media/<int:media_id>/", views.event_media_file, name="event_media_file"),
    path("events/media/<int:media_id>/remove/", views.delete_event_media, name="delete_event_media"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/<int:expense_id>/remove/", views.delete_expense, name="delete_expense"),
    path("crew/", views.crew_list, name="crew_list"),
    path("crew/<int:member_id>/remove/", views.delete_crew_member, name="delete_crew_member"),
    path("app.webmanifest", views.web_manifest, name="web_manifest"),
    path("service-worker.js", views.service_worker, name="service_worker"),
    path("offline/", views.offline_page, name="offline"),
    path("rsvp/<uuid:token>/", views.guest_rsvp, name="guest_rsvp"),
    path("guests/add/", views.add_guest, name="add_guest"),
    path("guests/fields/add/", views.add_guest_field, name="add_guest_field"),
    path(
        "guests/fields/<int:field_id>/remove/",
        views.delete_guest_field,
        name="delete_guest_field",
    ),
    path("guests/import/", views.import_guests, name="import_guests"),
    path("guests/<int:guest_id>/update/", views.update_guest, name="update_guest"),
    path("guests/export.csv", views.export_guests, name="export_guests"),
    path("guests/export.xlsx", views.export_excel, name="export_excel"),
    path("guests/template.xlsx", views.guest_template, name="guest_template"),
    path(
        "whatsapp/campaigns/queue/",
        views.queue_whatsapp_campaign,
        name="queue_whatsapp_campaign",
    ),
]
