from django.shortcuts import render

# render html for a request path
def home(request):
    return render(request, 'app/home.html')
