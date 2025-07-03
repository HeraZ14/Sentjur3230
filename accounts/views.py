from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages

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

class custom_login(LoginView):
    template_name = 'registration/login.html'
    def get(self, request, *args, **kwargs):
        if request.GET.get('logout') == '1':
            messages.success(request, "Odjava uspešna. Hvala za obisk metropole.")
        return super().get(request, *args, **kwargs)

class custom_logout(LogoutView):
    next_page = '/accounts/login/?logout=1'
