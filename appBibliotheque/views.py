from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from appBibliotheque.models import Livre,Emprunter,Exemplaire, Notification
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import send_notification
from django.core.paginator import Paginator 
from accounts.models import Utilisateur
from .models import Categorie
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserChangeForm

def home(request):
    livres = Livre.objects.order_by('id')
    paginator = Paginator(livres, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get user's borrowed books if authenticated
    emprunts = []
    if request.user.is_authenticated:
        emprunts = Emprunter.objects.filter(utilisateur=request.user , est_retourne = False).select_related('exemplaire__livre')

    # Fetch all categories
    categories = Categorie.objects.all()

    return render(request, 'appBibliotheque/user/home.html', {
        'page_obj': page_obj,
        'emprunts': emprunts,
        'categories': categories,
        'messages': messages.get_messages(request),
        'est_retourne': any(emprunt.est_retourne for emprunt in emprunts)  # Include est_retourne status
    })

# @login_required
def rechercher_livre(request):
    query = request.GET.get('titre')
    livres = []
    message=""
    if query:
        livres = Livre.objects.filter(titre__icontains=query)
        paginator = Paginator(livres, 16)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        message = "No search query provided."

    return render(request, 'appBibliotheque/user/home.html', {'page_obj': page_obj if query else None, 'query': query, 'message': message})
      
def detail_livre(request,slug):
    livre = get_object_or_404(Livre,slug=slug)
    return render(request,'appBibliotheque/user/unLivre.html',{"livre_detail":livre})


@login_required
def emprunter_exemplaire(request, slug):
    livre = get_object_or_404(Livre, slug=slug)
    utilisateur = request.user

    # Vérifier si l'utilisateur a déjà emprunté ce livre et ne l'a pas encore retourné
    if Emprunter.objects.filter(utilisateur=utilisateur, exemplaire__livre=livre, est_retourne=False).exists():
        
        message_text = f"Vous avez déjà emprunté le livre '{livre.titre}'."
        messages.warning(request, message_text)
        send_notification(utilisateur, message_text, link=reverse('detail_livre', kwargs={'slug': livre.slug}))
        return redirect('detail_livre', slug=livre.slug)

    # Vérifier si des exemplaires sont disponibles
    exemplaires_disponibles = Exemplaire.objects.filter(livre=livre, disponible=True  )
    if exemplaires_disponibles.exists():
        exemplaire = exemplaires_disponibles.first()
        # Créer un nouvel emprunt
        emprunt = Emprunter.objects.create(exemplaire=exemplaire, utilisateur=utilisateur)
        # Mettre à jour la disponibilité de l'exemplaire
        # exemplaire.disponible = False
        exemplaire.save()
        message_text = f"L'exemplaire du livre '{livre.titre}' a été emprunté avec succès."
        messages.success(request, message_text)
        send_notification(utilisateur, message_text, link=reverse('detail_livre', kwargs={'slug': livre.slug}))
    else:
        message_text = f"Aucun exemplaire disponible pour le livre '{livre.titre}'."
        messages.error(request, message_text)
        send_notification(utilisateur, message_text, link=reverse('detail_livre', kwargs={'slug': livre.slug}))

    return redirect('detail_livre', slug=livre.slug)


def liste_livres(request):
    livres = Livre.objects.all()
    return render(request,'appBibliotheque/dashboard/livre.html',{'livres' : livres })

def page_ajout(request):
    return render(request, 'appBibliotheque/dashboard/ajouter.html')

def edit_livre(request,id):
    livre = get_object_or_404(Livre,id=id)
    return render(request,'appBibliotheque/dashboard/edit.html',{'livre' : livre })


def ajouter_livre(request):
    livres = Livre.objects.all()
    if request.method == 'POST':
        titre = request.POST.get('titre')
        auteur = request.POST.get('auteur')
        isbn = request.POST.get('isbn')
        categories = request.POST.get('categories')
        description = request.POST.get('description')
        image_couverture = request.FILES.get('image_couverture')
        livre = Livre(titre=titre, auteur=auteur, isbn=isbn,categories=categories, description=description, image_couverture=image_couverture)
        if titre and auteur and isbn and description and image_couverture:
            livre.save()
            messages.success(request, "Le livre a été ajouté avec succès.")
            return render(request,'appBibliotheque/dashboard/ajouter.html',{'livres' : livres })  # Assurez-vous que 'acceuileBli' est correct
        else:
            messages.error(request, "Le formulaire n'est pas valide. Veuillez corriger les erreurs.")
    else:
       return render(request, 'appBibliotheque/dashboard/ajouter.html', {'livres' : livres })
   
   
def supprimer_exemplaire(request,id):
    
    livre = get_object_or_404(Livre,id=id)
    exemplaires = Exemplaire.objects.filter(livre=livre,disponible = True)
    if exemplaires.exists():
        exemplaire = exemplaires.first()
        exemplaire.delete()
        return redirect('liste_livres')
    else:
        return redirect('liste_livres')
def ajouter_exemplaire(request, id):
    livre = get_object_or_404(Livre,id=id)
    exemplaire = Exemplaire.objects.create(livre = livre, disponible=True)
    exemplaire.save()
    return redirect('liste_livres')

def detailLivre(request,id):
    livre = get_object_or_404(Livre,id=id)
    exemplaires = Exemplaire.objects.filter(livre=livre)#disponible = True
    return render(request,'appBibliotheque/dashboard/detailLivre.html',{'livre':livre,'exemplaires':exemplaires })

def page_UnLivre(request):
    return render(request,'appBibliotheque/user/unLivre.html')

def filterLivre(request,genre):
    if genre == "all":
        livres = Livre.objects.order_by('id')
    else:
        livres = Livre.objects.order_by('id').filter(categories__nom__iexact=genre)
    
    paginator = Paginator(livres, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Fetch all categories
    categories = Categorie.objects.all()
    return render(request,'appBibliotheque/user/home.html', {'genre': genre, 'page_obj': page_obj , 'categories': categories ,}) 

from .decorators import librarian_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

@librarian_required
def dashboard(request):
    # Basic statistics
    nbUsers = Utilisateur.objects.filter(est_bibliothecaire=False).count()
    nbLivres = Livre.objects.count()
    nbEmpruntes = Emprunter.objects.count()
    nbExemplairePerdu = Exemplaire.objects.filter(perdu=True).count()
    
    # Recent activity
    recent_emprunts = Emprunter.objects.select_related('utilisateur', 'exemplaire__livre').order_by('-date_emprunt')[:5]
    
    # Monthly borrowing statistics
    today = datetime.now()
    six_months_ago = today - timedelta(days=180)
    monthly_stats = Emprunter.objects.filter(
        date_emprunt__gte=six_months_ago
    ).annotate(
        month=TruncMonth('date_emprunt')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Most borrowed books
    popular_books = Livre.objects.annotate(
        borrow_count=Count('exemplaires_livre__emprunter')
    ).order_by('-borrow_count')[:5]
    
    context = {
        "nbUsers": nbUsers,
        "nbLivres": nbLivres,
        "nbEmpruntes": nbEmpruntes,
        "nbExemplairePerdu": nbExemplairePerdu,
        "recent_emprunts": recent_emprunts,
        "monthly_stats": monthly_stats,
        "popular_books": popular_books
    }
    return render(request, 'appBibliotheque/dashboard/dashboard.html', context)

def about_us(request):
    return render(request, 'appBibliotheque/user/about.html')

def contact_us(request):
    return render(request, 'appBibliotheque/user/contact.html')

@login_required
def profile(request):
    # Get user's active borrowings
    emprunts = Emprunter.objects.filter(utilisateur=request.user ,  est_retourne = False).select_related('exemplaire__livre')

    context = {
        'user': request.user,
        'emprunts': emprunts,
    }

    return render(request, 'appBibliotheque/user/profile.html', context)


@login_required
def view_all_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark all as read when viewing all
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/all_notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def clear_all_notifications(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

from django.shortcuts import render, redirect
from .forms import ProfileEditForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            user = form.save()
            
            # Handle password change if provided
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if old_password and new_password1 and new_password2:
                if new_password1 == new_password2:
                    if request.user.check_password(old_password):
                        request.user.set_password(new_password1)
                        request.user.save()
                        update_session_auth_hash(request, request.user)  # Important to keep the user logged in
                        messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
                    else:
                        messages.error(request, 'Votre ancien mot de passe est incorrect.')
                else:
                    messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
            
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'appBibliotheque/user/edit_profile.html')

@login_required
def return_book(request, emprunt_id):
    emprunt = get_object_or_404(Emprunter, id=emprunt_id, utilisateur=request.user)

    if not emprunt.est_retourne:
        emprunt.est_retourne = True
        emprunt.exemplaire.disponible = True
        emprunt.exemplaire.est_retourne = True
        emprunt.exemplaire.save()
        emprunt.save()
        # emprunt.exemplaire.delete()
        # emprunt.delete()

        messages.success(request, f"Le livre '{emprunt.exemplaire.livre.titre}' a été retourné avec succès.")
    else:
        messages.warning(request, f"Le livre '{emprunt.exemplaire.livre.titre}' a déjà été retourné.")

    return redirect('profile')



    def addnewuser(request):
        # if method == post:
        pass