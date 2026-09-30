from django.urls import path

from . import views


urlpatterns = [
    path("", views.organizer_signup, name="organizer_signup"),
]
