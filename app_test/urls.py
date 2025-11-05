from django.urls import path
from .views import aws_test_view

urlpatterns = [
    path("aws-test/", aws_test_view, name="aws-test"),
]
