from django.contrib.auth.views import LogoutView, LoginView, PasswordResetDoneView, PasswordResetCompleteView
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
            messages.warning(request, "Podatki so manjkajoči ali pa jih ni.")
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

    def form_invalid(self, form):
        messages.error(self.request, "Nepravilno uporabniško ime ali geslo.")
        return super().form_invalid(form)

class custom_logout(LogoutView):
    next_page = '/accounts/login/?logout=1'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get(self, request, *args, **kwargs):
        messages.success(request, "Če si pravilno vpisal e-mail naslov, si dobil navodila za ponastavitev gesla v tvoj poštni nabiralnik.")
        return super().get(request, *args, **kwargs)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request, *args, **kwargs):
        messages.success(request, "Vaše geslo je bilo uspešno ponastavljeno. Sedaj se lahko prijavite")
        return super().get(request, *args, **kwargs)
