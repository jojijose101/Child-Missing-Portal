from django.urls import path

from . import views

urlpatterns = [
        path("user-upload/", views.user_upload_and_match, name="user_upload"),
        path("admin-upload/", views.admin_upload, name="admin_upload"),

]