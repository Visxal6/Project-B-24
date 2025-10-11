from django.shortcuts import render
from django.http import HttpResponse

# render html for a request path
def home(request):
    return render(request, 'app/home.html')
