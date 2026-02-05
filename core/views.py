from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .ai.face_detect import detect_face
from .ai.face_embed import get_embedding
from .ai.matcher import find_best_match
import pickle
from django.shortcuts import render
from django.http import HttpResponse
from .models import MissingChild
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views.decorators.http import require_POST
import os
import csv
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import PoliceStation, StationProfile
from .models import MissingChild, Report


def station_add_case(request):
    if not request.user.is_authenticated:
        return redirect("station_login")

    profile = StationProfile.objects.get(user=request.user)

    if request.method == "GET":
        return render(request, "station/add_case.html")

    # POST
    child_name = request.POST.get("child_name", "").strip()
    age = request.POST.get("age") or None
    last_seen_location = request.POST.get("last_seen_location", "").strip()
    details = request.POST.get("details", "").strip()
    uploaded_img = request.FILES.get("image")

    if not child_name or not last_seen_location or not uploaded_img:
        return render(
            request,
            "station/add_case.html",
            {"error": "Please fill all required fields."},
        )

    if not uploaded_img.content_type.startswith("image"):
        return render(
            request, "station/add_case.html", {"error": "Upload a valid image file."}
        )

    # Save image in media
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    saved_name = fs.save(f"missing_children/{uploaded_img.name}", uploaded_img)
    image_path = os.path.join(settings.MEDIA_ROOT, saved_name)

    # Detect face (RGB)
    face_rgb = detect_face(image_path)
    if face_rgb is None:
        return render(
            request,
            "station/add_case.html",
            {"error": "No face detected. Upload a clearer image."},
        )

    # Create embedding
    emb = get_embedding(face_rgb)

    # Save case in DB
    MissingChild.objects.create(
        station=profile.station,
        child_name=child_name,
        age=age,
        last_seen_location=last_seen_location,
        details=details,
        image=saved_name,
        embedding=pickle.dumps(emb),
        status="missing",
    )

    return render(
        request, "station/add_case.html", {"msg": "Missing case saved successfully ✅"}
    )


def public_report(request):
    if request.method == "GET":
        return render(request, "public/report_upload.html")

    # POST
    reporter_name = request.POST.get("reporter_name", "").strip()
    reporter_phone = request.POST.get("reporter_phone", "").strip()
    found_location = request.POST.get("found_location", "").strip()
    notes = request.POST.get("notes", "").strip()

    uploaded_img = request.FILES.get("image")
    if not (reporter_name and reporter_phone and found_location and uploaded_img):
        return render(
            request,
            "public/report_upload.html",
            {"error": "Please fill all required fields."},
        )

    if not uploaded_img.content_type.startswith("image"):
        return render(
            request,
            "public/report_upload.html",
            {"error": "Upload a valid image file."},
        )

    # Save image
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    saved_name = fs.save(f"reports/{uploaded_img.name}", uploaded_img)
    image_path = os.path.join(settings.MEDIA_ROOT, saved_name)

    # Face detect
    face_rgb = detect_face(image_path)
    if face_rgb is None:
        return render(
            request,
            "public/report_upload.html",
            {"error": "No face detected. Upload a clearer image."},
        )

    # Embedding
    query_emb = get_embedding(face_rgb)

    # Match (threshold can be adjusted)
    cases = MissingChild.objects.all()
    matched_case, best_dist = find_best_match(query_emb, cases, threshold=1.0)

    # Save report record always
    report = Report.objects.create(
        reporter_name=reporter_name,
        reporter_phone=reporter_phone,
        found_location=found_location,
        notes=notes,
        image=saved_name,
    )

    if matched_case is not None:
        report.matched_case = matched_case
        report.matched_station = matched_case.station
        report.distance = float(best_dist)
        report.status = "matched"
        report.is_seen_by_station = False
        report.save()

        return render(
            request,
            "public/report_result.html",
            {
                "matched": True,
                "distance": round(float(best_dist), 4),
                "child": matched_case,
                "station": matched_case.station,
            },
        )

    report.distance = float(best_dist)
    report.status = "unmatched"
    report.save()

    return render(
        request,
        "public/report_result.html",
        {
            "matched": False,
            "distance": round(float(best_dist), 4),
        },
    )


def station_reports(request):
    if not request.user.is_authenticated:
        return redirect("station_login")

    profile = StationProfile.objects.get(user=request.user)

    reports = (
        Report.objects.filter(matched_station=profile.station, status="matched")
        .select_related("matched_case")
        .order_by("-created_at")
    )

    return render(
        request,
        "station/reports_list.html",
        {"station": profile.station, "reports": reports},
    )


def station_report_detail(request, report_id):
    if not request.user.is_authenticated:
        return redirect("station_login")

    profile = StationProfile.objects.get(user=request.user)

    report = get_object_or_404(Report, id=report_id, matched_station=profile.station)

    # ✅ mark seen (notification removed)
    if not report.is_seen_by_station:
        report.is_seen_by_station = True
        report.save(update_fields=["is_seen_by_station"])

    return render(request, "station/report_detail.html", {"report": report})


def station_auth_page(request):
    return render(request, "station/auth.html", {"open": "login"})


def station_signup(request):
    if request.method == "GET":
        return render(request, "station/auth.html", {"open": "signup"})

    station_name = request.POST.get("station_name", "").strip()
    address = request.POST.get("address", "").strip()
    phone = request.POST.get("phone", "").strip()
    email = request.POST.get("email", "").strip() or None

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password1", "").strip()
    password2 = request.POST.get("password2", "").strip()

    if not (station_name and address and phone and username and password and password2):
        return render(
            request,
            "station/auth.html",
            {"error": "All required fields must be filled.", "open": "signup"},
        )

    if password != password2:
        return render(
            request,
            "station/auth.html",
            {"error": "Passwords do not match.", "open": "signup"},
        )

    if PoliceStation.objects.filter(name__iexact=station_name).exists():
        return render(
            request,
            "station/auth.html",
            {"error": "This station already has an account.", "open": "signup"},
        )

    try:
        user = User.objects.create_user(username=username, password=password)
    except IntegrityError:
        return render(
            request,
            "station/auth.html",
            {"error": "Username already taken. Choose another.", "open": "signup"},
        )

    station = PoliceStation.objects.create(
        name=station_name, address=address, phone=phone, email=email
    )
    StationProfile.objects.create(user=user, station=station)

    return render(
        request,
        "station/auth.html",
        {"msg": "Station account created successfully. Please login.", "open": "login"},
    )


def station_login(request):
    if request.method == "GET":
        return render(request, "station/auth.html", {"open": "login"})

    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)
    if user is None:
        return render(
            request,
            "station/auth.html",
            {"login_error": "Invalid username or password.", "open": "login"},
        )

    if not StationProfile.objects.filter(user=user).exists():
        return render(
            request,
            "station/auth.html",
            {"login_error": "This account is not a station account.", "open": "login"},
        )

    login(request, user)
    return redirect("station_dashboard")


def station_logout(request):
    logout(request)
    return redirect("station_auth_page")


@login_required
def station_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("station_login")

    profile = StationProfile.objects.get(user=request.user)
    total_cases = MissingChild.objects.filter(station=profile.station).count()
    total_missing = MissingChild.objects.filter(
        station=profile.station, status="missing"
    ).count()
    total_found = MissingChild.objects.filter(
        station=profile.station, status="found"
    ).count()

    q = request.GET.get("q", "").strip()
    show_found = request.GET.get("show_found") == "1"

    cases = MissingChild.objects.filter(station=profile.station)

    # 🔍 search filter
    if q:
        cases = cases.filter(
            Q(child_name__icontains=q) | Q(last_seen_location__icontains=q)
        )

    # 👁️ hide FOUND by default
    if not show_found:
        cases = cases.filter(status="missing")

    cases = cases.order_by("-created_at")

    new_matches = Report.objects.filter(
        matched_station=profile.station, status="matched", is_seen_by_station=False
    ).count()

    for c in cases:
        c.new_match_count = Report.objects.filter(
            matched_case=c, status="matched", is_seen_by_station=False
        ).count()

    return render(
        request,
        "station/dashboard.html",
        {
            "station": profile.station,
            "cases": cases,
            "new_matches": new_matches,
            "q": q,
            "show_found": show_found,
            "total_cases": total_cases,
            "total_missing": total_missing,
            "total_found": total_found,
        },
    )


def station_case_detail(request, case_id):
    if not request.user.is_authenticated:
        return redirect("station_login")

    profile = StationProfile.objects.get(user=request.user)

    case = get_object_or_404(MissingChild, id=case_id, station=profile.station)

    reports = Report.objects.filter(matched_case=case, status="matched").order_by(
        "-created_at"
    )

    return render(
        request, "station/case_detail.html", {"case": case, "reports": reports}
    )


@require_POST
def station_case_mark_found(request, case_id):
    if not request.user.is_authenticated:
        return redirect("station_login")

    profile = StationProfile.objects.get(user=request.user)

    case = get_object_or_404(MissingChild, id=case_id, station=profile.station)

    case.status = "found"
    case.save(update_fields=["status"])

    # Optional: mark all related matched reports as seen
    Report.objects.filter(
        matched_case=case, status="matched", is_seen_by_station=False
    ).update(is_seen_by_station=True)

    return redirect("station_case_detail", case_id=case.id)


def station_export_cases_csv(request):
    if not request.user.is_authenticated:
        return redirect("station_login")

    profile = StationProfile.objects.get(user=request.user)

    q = request.GET.get("q", "").strip()
    show_found = request.GET.get("show_found") == "1"

    cases = MissingChild.objects.filter(station=profile.station)

    if q:
        cases = cases.filter(
            Q(child_name__icontains=q) | Q(last_seen_location__icontains=q)
        )

    if not show_found:
        cases = cases.filter(status="missing")

    cases = cases.order_by("-created_at")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="cases_export.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Child Name",
            "Age",
            "Last Seen Location",
            "Status",
            "Created At",
            "Image Path",
        ]
    )

    for c in cases:
        writer.writerow(
            [
                c.id,
                c.child_name,
                c.age or "",
                c.last_seen_location,
                c.status,
                c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                c.image.name,  # file path inside MEDIA
            ]
        )

    return response


def station_graph_report(request):
    if not request.user.is_authenticated:
        return redirect("station_login")

    profile = StationProfile.objects.get(user=request.user)
    station = profile.station

    # --- Bar chart: missing vs found
    missing_count = MissingChild.objects.filter(
        station=station, status="missing"
    ).count()
    found_count = MissingChild.objects.filter(station=station, status="found").count()

    # --- Line chart: matched reports per day (last 7 days)
    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    qs = (
        Report.objects.filter(
            matched_station=station, status="matched", created_at__date__gte=start_date
        )
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # Build full 7-day series (fill missing days with 0)
    day_map = {row["day"]: row["total"] for row in qs}
    labels = []
    values = []
    for i in range(7):
        d = start_date + timedelta(days=i)
        labels.append(d.strftime("%d-%b"))  # e.g. 04-Feb
        values.append(day_map.get(d, 0))

    return render(
        request,
        "station/graph_report.html",
        {
            "missing_count": missing_count,
            "found_count": found_count,
            "labels": labels,
            "values": values,
        },
    )
