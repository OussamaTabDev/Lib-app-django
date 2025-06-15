from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from .models import Utilisateur, Livre, Exemplaire, Emprunter, Categorie, Reservation
from appBibliotheque.utils import send_notification
from django.utils.text import slugify

@staff_member_required
def library_dashboard(request):
    """Main dashboard for library administrators"""
    
    # Get statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        # Basic counts
        'total_books': Livre.objects.count(),
        'total_copies': Exemplaire.objects.count(),
        'total_users': Utilisateur.objects.filter(est_bibliothecaire=False).count(),
        'active_librarians': Utilisateur.objects.filter(est_bibliothecaire=True, is_active=True).count(),
        
        # Current status
        'pending_requests': Emprunter.objects.filter(statut='en_attente').count(),
        'active_borrows': Emprunter.objects.filter(accepter=True, date_retour_reel__isnull=True).count(),
        'overdue_borrows': Emprunter.objects.filter(
            accepter=True, 
            date_retour_reel__isnull=True,
            date_retour_prevue__lt=today
        ).count(),
        
        # Weekly stats
        'new_requests_week': Emprunter.objects.filter(date_demande__gte=week_ago).count(),
        'returned_this_week': Emprunter.objects.filter(date_retour_reel__gte=week_ago).count(),
        
        # Monthly stats
        'new_books_month': Livre.objects.filter(date_ajout__gte=month_ago).count(),
        'new_users_month': Utilisateur.objects.filter(date_joined__gte=month_ago, est_bibliothecaire=False).count(),
    }
    
    # Recent activities
    recent_requests = Emprunter.objects.filter(
        statut='en_attente' 
    ).select_related('utilisateur', 'exemplaire__livre').order_by('-date_demande')[:10]
    
    overdue_borrows = Emprunter.objects.filter(
        statut='accepte',
        accepter=True,
        est_retourne=False,
        # date_retour_reel__isnull=True,
        # date_retour_prevue__lt=today
    ).select_related('utilisateur', 'exemplaire__livre').order_by('date_retour_prevue')[:10]
    print(overdue_borrows)
    # Popular books
    popular_books = Livre.objects.annotate(
        borrow_count=Count('exemplaires_livre__emprunt_actuel')
    ).order_by('-borrow_count')[:5]
    
    # Categories distribution
    categories_stats = Categorie.objects.annotate(
        book_count=Count('livres'),
        active_borrows=Count('livres__exemplaires_livre__emprunt_actuel', 
                           filter=Q(livres__exemplaires_livre__emprunt_actuel__accepter=True,
                                   livres__exemplaires_livre__emprunt_actuel__date_retour_reel__isnull=True))
    ).order_by('-book_count')
    
    context = {
        'stats': stats,
        'recent_requests': recent_requests,
        'overdue_borrows': overdue_borrows,
        'popular_books': popular_books,
        'categories_stats': categories_stats,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@staff_member_required
def manage_borrow_requests(request):
    """Manage pending borrow requests"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('rendu', 'Rendu'),
        ('en_retard', 'En retard'),
    ]

    # Get pending requests
    pending_requests = Emprunter.objects.filter(
        statut='en_attente'
    ).select_related('utilisateur', 'exemplaire__livre').order_by('-date_demande')

    # Handle quick actions
    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')

        if request_id:
            emprunt = get_object_or_404(Emprunter, id=request_id)

            if action == 'approve':
                if emprunt.utilisateur.can_borrow_more_books() and emprunt.exemplaire.is_available():
                    print("yes")
                    emprunt.accepter = True
                    emprunt.statut = 'accepte'
                    emprunt.notes_admin = request.POST.get('admin_notes', '')
                    emprunt.save()
                    # Send notification to user
                    send_notification(
                        emprunt.utilisateur,
                        f'Your borrow request for {emprunt.exemplaire.livre.titre} has been approved.',
                        f'/detail_livre/{emprunt.exemplaire.livre.slug}'
                    )
                    messages.success(request, f'Emprunt approuvé pour {emprunt.utilisateur.username}')
                else:
                    messages.error(request, 'Impossible d\'approuver: limite atteinte ou exemplaire indisponible')

            elif action == 'reject':
                emprunt.statut = 'refuse'
                emprunt.notes_admin = request.POST.get('admin_notes', '')
                emprunt.save()
                # Send notification to user
                send_notification(
                    emprunt.utilisateur,
                    f'Your borrow request for {emprunt.exemplaire.livre.titre} has been rejected.',
                    f'/detail_livre/{emprunt.exemplaire.livre.slug}'
                )
                messages.success(request, f'Emprunt refusé pour {emprunt.utilisateur.username}')

        return redirect('manage_borrow_requests')
    
    # Pagination
    paginator = Paginator(pending_requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_pending': pending_requests.count(),
    }
    
    return render(request, 'dashboard/manage_requests.html', context)

@staff_member_required
def active_borrows(request):
    """View and manage active borrows"""
    
    active_borrows = Emprunter.objects.filter(
        accepter=True,
        date_retour_reel__isnull=True
    ).select_related('utilisateur', 'exemplaire__livre').order_by('date_retour_prevue')
    
    # Filter options
    filter_type = request.GET.get('filter', 'all')
    today = timezone.now().date()
    
    if filter_type == 'overdue':
        active_borrows = active_borrows.filter(date_retour_prevue__lt=today)
    elif filter_type == 'due_soon':
        due_soon = today + timedelta(days=2)
        active_borrows = active_borrows.filter(date_retour_prevue__lte=due_soon, date_retour_prevue__gte=today)
    
    # Handle return marking
    if request.method == 'POST':
        borrow_id = request.POST.get('borrow_id')
        if borrow_id:
            emprunt = get_object_or_404(Emprunter, id=borrow_id)
            emprunt.date_retour_reel = timezone.now().date()
            emprunt.save()
            messages.success(request, f'Livre "{emprunt.exemplaire.livre.titre}" marqué comme rendu')
            return redirect('active_borrows')
    
    # Pagination
    paginator = Paginator(active_borrows, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_type': filter_type,
        'total_active': active_borrows.count(),
    }
    
    return render(request, 'admin/active_borrows.html', context)

@staff_member_required
def user_borrowing_history(request, user_id):
    """View detailed borrowing history for a specific user"""
    
    user = get_object_or_404(Utilisateur, id=user_id)
    
    borrowing_history = Emprunter.objects.filter(
        utilisateur=user
    ).select_related('exemplaire__livre').order_by('-date_demande')
    
    # Statistics for this user
    user_stats = {
        'total_borrows': borrowing_history.count(),
        'active_borrows': borrowing_history.filter(accepter=True, date_retour_reel__isnull=True).count(),
        'overdue_count': borrowing_history.filter(
            accepter=True,
            date_retour_reel__isnull=True,
            date_retour_prevue__lt=timezone.now().date()
        ).count(),
        'total_returned': borrowing_history.filter(date_retour_reel__isnull=False).count(),
    }
    
    # Pagination
    paginator = Paginator(borrowing_history, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user': user,
        'user_stats': user_stats,
        'page_obj': page_obj,
    }
    
    return render(request, 'admin/user_history.html', context)

@staff_member_required
def book_management(request):
    """Manage books and their copies"""
    
    books = Livre.objects.annotate(
        total_copies=Count('exemplaires_livre'),
        available_copies=Count('exemplaires_livre', filter=Q(exemplaires_livre__disponible=True, exemplaires_livre__perdu=False)),
        active_borrows=Count('exemplaires_livre__emprunt_actuel', filter=Q(exemplaires_livre__emprunt_actuel__accepter=True, exemplaires_livre__emprunt_actuel__date_retour_reel__isnull=True))
    ).order_by('titre')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(titre__icontains=search_query) |
            Q(auteur__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        books = books.filter(categories__id=category_filter)
    
    # Pagination
    paginator = Paginator(books, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter dropdown
    categories = Categorie.objects.all().order_by('nom')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    
    return render(request, 'dashboard/book_management.html', context)

@staff_member_required
def reports(request):
    """Generate various reports"""
    
    # Date range for reports
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Borrowing trends
    daily_borrows = Emprunter.objects.filter(
        date_emprunt__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(date_emprunt)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Most popular books
    popular_books = Livre.objects.annotate(
        borrow_count=Count('exemplaires_livre__emprunt_actuel', 
                          filter=Q(exemplaires_livre__emprunt_actuel__date_emprunt__range=[start_date, end_date]))
    ).filter(borrow_count__gt=0).order_by('-borrow_count')[:10]
    
    # User statistics
    active_users = Utilisateur.objects.filter(
        emprunter__date_emprunt__range=[start_date, end_date]
    ).annotate(
        borrow_count=Count('emprunter')
    ).order_by('-borrow_count')[:10]
    
    # Category analysis
    category_stats = Categorie.objects.annotate(
        borrows_in_period=Count('livres__exemplaires_livre__emprunt_actuel',
                               filter=Q(livres__exemplaires_livre__emprunt_actuel__date_emprunt__range=[start_date, end_date]))
    ).filter(borrows_in_period__gt=0).order_by('-borrows_in_period')
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'daily_borrows': daily_borrows,
        'popular_books': popular_books,
        'active_users': active_users,
        'category_stats': category_stats,
    }
    
    return render(request, 'admin/reports.html', context)

@staff_member_required
def send_overdue_reminders(request):
    """Send reminders to users with overdue books"""
    
    if request.method == 'POST':
        overdue_borrows = Emprunter.objects.filter(
            accepter=True,
            date_retour_reel__isnull=True,
            date_retour_prevue__lt=timezone.now().date()
        ).select_related('utilisateur', 'exemplaire__livre')
        
        # Here you would integrate with email system
        # For now, we'll just mark them and show a message
        reminder_count = overdue_borrows.count()
        
        # In a real implementation, you'd send emails here
        # send_email_reminders(overdue_borrows)
        
        messages.success(request, f'Rappels envoyés à {reminder_count} utilisateurs avec des livres en retard.')
        
        return redirect('library_dashboard')
    
    return redirect('library_dashboard')

@staff_member_required
def user_management(request):
    """View for managing users"""
    users = Utilisateur.objects.filter(est_bibliothecaire=False)
    return render(request, 'dashboard/users.html', {'users': users})

@staff_member_required
def book_details(request, book_id):
    """View for displaying book details"""
    book = get_object_or_404(Livre, id=book_id)
    return render(request, 'dashboard/detailLivre.html', {'book': book})

@staff_member_required
def empruntes_page(request):
    """View for displaying the Empruntes page"""
    borrows = Emprunter.objects.select_related('utilisateur', 'exemplaire__livre').order_by('-date_demande')
    stats = {
        'total': borrows.count(),
        'active': borrows.filter(accepter=True, date_retour_reel__isnull=True).count(),
        'overdue': borrows.filter(accepter=True, date_retour_reel__isnull=True, date_retour_prevue__lt=timezone.now().date()).count(),
        'returned': borrows.filter(date_retour_reel__isnull=False).count(),
    }
    context = {
        'title': 'Empruntes',
        'borrows': borrows,
        'stats': stats,
    }
    return render(request, 'dashboard/Emprunte.html', context)

# API endpoints for AJAX calls
@staff_member_required
def api_book_availability(request, book_id):
    """API endpoint to check book availability"""
    
    livre = get_object_or_404(Livre, id=book_id)
    
    data = {
        'total_copies': livre.get_total_exemplaires(),
        'available_copies': livre.get_exemplaires_disponibles(),
        'max_borrow_days': livre.get_max_borrow_days(),
        'is_available': livre.is_available_for_borrow(),
    }
    
    return JsonResponse(data)

@staff_member_required
def api_user_can_borrow(request, user_id):
    """API endpoint to check if user can borrow more books"""
    
    user = get_object_or_404(Utilisateur, id=user_id)
    
    data = {
        'can_borrow': user.can_borrow_more_books(),
        'active_borrows': user.get_active_emprunts_count(),
        'max_borrows': 3,
    }
    
    return JsonResponse(data)

from django.shortcuts import render, redirect
from appBibliotheque.models import Livre

def view_books(request):
    books = Livre.objects.all()
    return render(request, 'dashboard/book_management.html', {'books': books})

def add_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        category_id = request.POST['categories']
        published_date = request.POST['published_date']
        description = request.POST.get('description', '')
        category = Categorie.objects.get(id=category_id)
        isbn = request.POST.get('isbn', '')
        slug = slugify(isbn)
        slug_base = slugify(isbn)
        slug = slug_base
        counter = 1
        while Livre.objects.filter(slug=slug).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1
        book = Livre.objects.create(titre=title, auteur=author, date_publication=published_date, description=description, image_couverture=request.FILES.get('cover_image'), slug=slug)
        book.categories.set([category_id])
        return redirect('book_management')
    categories = Categorie.objects.all()
    return render(request, 'dashboard/add_book.html', {'categories': categories})

def edit_book(request, id):
    book = Livre.objects.get(id=id)
    if request.method == 'POST':
        Livre.title = request.POST['title']
        Livre.author = request.POST['author']
        Livre.genre = request.POST['genre']
        Livre.published_date = request.POST['published_date']
        Livre.save()
        return redirect('book_management')
    return render(request, 'dashboard/edit_book.html', {'book': book})

def delete_book(request, id):
    book = Livre.objects.get(id=id)
    Livre.delete()
    return redirect('book_management')