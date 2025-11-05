from django.shortcuts import render, redirect
from .models import TestImage

# Create your views here.


def aws_test_view(request):
    if request.method == "POST" and "image" in request.FILES:
        # Save image
        img = TestImage.objects.create(image=request.FILES["image"])
        return redirect("aws-test")

    # Get all image in TestImage table
    images = TestImage.objects.all().order_by("-uploaded_at")

    # Respond with html and images
    return render(request, "app_test/aws_test.html",      {"images": images})
