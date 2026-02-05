from django.urls import path

from . import views

urlpatterns = [
    path("station/signup/", views.station_signup, name="station_signup"),
    path("station/login/", views.station_login, name="station_login"),
    path("station/logout/", views.station_logout, name="station_logout"),
    path("station/dashboard/", views.station_dashboard, name="station_dashboard"),
    path("station/cases/add/", views.station_add_case, name="station_add_case"),
    path("report/", views.public_report, name="public_report"),
    path("station/reports/", views.station_reports, name="station_reports"),
    path(
        "station/reports/<int:report_id>/",
        views.station_report_detail,
        name="station_report_detail",
    ),
    path(
        "station/cases/<int:case_id>/",
        views.station_case_detail,
        name="station_case_detail",
    ),
    path(
        "station/cases/<int:case_id>/mark-found/",
        views.station_case_mark_found,
        name="station_case_mark_found",
    ),
    path(
        "station/cases/export/",
        views.station_export_cases_csv,
        name="station_export_cases_csv",
    ),
    path(
        "station/reports/graph/",
        views.station_graph_report,
        name="station_graph_report",
    ),
    path("station/auth/", views.station_auth_page, name="station_auth_page"),
]
