from django.shortcuts import render

# Create your views here.
from .ai.face_detect import detect_face
from .ai.face_embed import get_embedding
from .ai.matcher import find_best_match
import pickle
from django.shortcuts import render
from django.http import HttpResponse
from .models import MissingChild
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def save_image(uploaded_file):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    filename = fs.save(uploaded_file.name, uploaded_file)
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    return file_path

def admin_upload(request):
    if request.method == "POST":
        img = request.FILES['image']
        path = save_image(img)

        face = detect_face(path)
        if face is None:
            return HttpResponse("No face detected")

        embedding = get_embedding(face)

        MissingChild.objects.create(
            name=request.POST['name'],
            age=request.POST['age'],
            location=request.POST['location'],
            image=img,
            embedding=pickle.dumps(embedding)
        )

        return HttpResponse("Child Added Successfully")
    return render(request, "admin_upload.html")



def user_upload_and_match(request):
    if request.method == "GET":
        return render(request, "user_upload.html")

    # POST
    uploaded_img = request.FILES.get("image")
    if not uploaded_img or not uploaded_img.content_type.startswith("image"):
        return render(request, "user_upload.html", {"error": "Please upload a valid image file."})

    # Save temporarily so OpenCV can read it
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    saved_name = fs.save(f"queries/{uploaded_img.name}", uploaded_img)
    image_path = os.path.join(settings.MEDIA_ROOT, saved_name)

    # Face detect
    face = detect_face(image_path)
    if face is None:
        return render(request, "user_upload.html", {"error": "No face detected. Try another image."})

    # Embedding
    query_emb = get_embedding(face)

    # Match with DB
    children = MissingChild.objects.all()
    matched_child, best_dist = find_best_match(query_emb, children, threshold=1.0)

    if matched_child:
        # OPTIONAL: update status
        matched_child.status = "found"
        matched_child.save(update_fields=["status"])

        return render(request, "match_result.html", {
            "matched": True,
            "child": matched_child,
            "distance": round(float(best_dist), 4),
            "uploaded_image": settings.MEDIA_URL + saved_name,
        })

    # No match
    return render(request, "match_result.html", {
        "matched": False,
        "distance": round(float(best_dist), 4),
        "uploaded_image": settings.MEDIA_URL + saved_name,
    })