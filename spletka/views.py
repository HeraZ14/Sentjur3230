from django.shortcuts import render, redirect

from spletka.forms import IdeaForm


def home(request):
    return render(request, 'home.html',{})


def kontakt(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'kontakt.html')
    else:
        form = IdeaForm()

    return render(request, 'kontakt.html',{})