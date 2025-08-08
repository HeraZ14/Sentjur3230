from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LogoutView, LoginView, PasswordResetDoneView, PasswordResetCompleteView
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from store.models import Order

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
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-date')
    password_form = PasswordChangeForm(request.user)

    return render(request, 'registration/profile.html', {
        'orders': orders,
        'password_form': password_form,
    })

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

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Tvoj račun je bil uspešno izbrisan.")
        return redirect('home')  # ali kamor želiš preusmeriti

    # Če ni POST, potem samo prikažemo potrditveni obrazec
    return render(request, 'registration/delete_account.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # ohrani login
            messages.success(request, 'Geslo uspešno spremenjeno.')
            return redirect('profile')
        else:
            messages.error(request, 'Popravi napake spodaj.')
    return redirect('profile')