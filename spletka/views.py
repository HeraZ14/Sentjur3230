from django.shortcuts import render

def home(request):
    return render(request, 'home.html',{})


def kontakt(request):
    return render(request, 'kontakt.html',{})