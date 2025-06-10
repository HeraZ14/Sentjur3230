from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # avtomatska prijava
            return redirect('vojzek')  # ali kamorkoli
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')

def custom_login(request):
    return render(request, 'registration/login.html')

def custom_logout(request):
    logout(request)
    return render(request, 'registration/logout.html')
