from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from spletka.forms import IdeaForm
from .models import Page


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


def preview_page(request, slug):
    token = request.GET.get("token")
    page = get_object_or_404(Page, slug=slug)

    if page.is_published or token == page.preview_token:
        return render(request, "home.html", {"page": page})

    raise Http404("Neveljaven token ali stran ne obstaja.")