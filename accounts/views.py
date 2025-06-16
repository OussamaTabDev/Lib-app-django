from sqlite3 import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login as auth_login, logout, authenticate # Renamed login to auth_login to avoid conflict
# from django.contrib.auth import authenticate, login # Duplicate import
# from django.contrib.auth.models import User # Not used directly, get_user_model is preferred
from .models import Utilisateur
# from django.contrib.auth.forms import PasswordResetForm # Not used in this specific view
from urllib.parse import unquote
from .forms import RegistrationForm # Import the new form

User = get_user_model()

# Existing register view (might be replaced later)
def register(request):
    return render(request,'accounts/register.html')

# New registration view using RegistrationForm
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user) # Use the aliased login function
            return redirect('home')  # Assuming 'home' is a valid URL name
        else:
            # Form is invalid, render again with errors
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


# Existing signup view (manual implementation)
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password mismatch
        if password != confirm_password:
            return render(request, 'accounts/register.html', {
                'error': 'Les mots de passe ne correspondent pas',
                'username': username,
                'email': email
            })

        # Check for existing username
        if Utilisateur.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Ce nom d’utilisateur existe déjà.',
                'email': email
            })

        # Check for existing email
        if Utilisateur.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Cet email est déjà utilisé.',
                'username': username
            })

        try:
            user = Utilisateur.objects.create_user(username=username, email=email, password=password)
            # user.save() # create_user already saves
            # user = authenticate(username=username, password=password) # Not needed right after creation if password is set
            auth_login(request, user) # Use the aliased login function
            return redirect('home')
        except IntegrityError: # This might not be the right exception for create_user, which handles IntegrityError internally
            return render(request, 'accounts/register.html', {
                'error': 'Une erreur s’est produite. Veuillez réessayer.'
            })

    # If GET or other methods, or if POST processing falls through without redirecting
    return render(request, 'accounts/register.html')

def pagelogin(request):
    return render(request,'accounts/login.html')

def login_user(request):
    error=""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user) # Use the aliased login function
            return redirect('home')
        else:
            # Gérer le cas où l'authentification échoue
            error ='Invalid username or password'
            return render(request, 'accounts/login.html', {'error': error })

    return render(request, 'accounts/login.html')

def logout_user(request):#champs à definir
    logout(request)
    return redirect('home')

def users_lists(request):
    users = Utilisateur.objects.all()
    return render(request, 'dashboard/users.html', {'users': users})


def delete_user(request,username):
    #users = users = Utilisateur.objects.all()
    decoded_username = unquote(username)
    u_username = get_object_or_404(Utilisateur,username=decoded_username)
    if u_username and u_username.est_bibliothecaire == False:   
        u_username.delete()
    return redirect('users_lists')
