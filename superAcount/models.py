from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib import messages
from django.shortcuts import redirect
from accounts.models import Utilisateur 
from appBibliotheque.models import  Livre, Exemplaire, Emprunter , Categorie , Reservation



# Custom User Admin
# @admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'est_bibliothecaire', 'active_borrows_count', 'is_active')
    list_filter = ('est_bibliothecaire', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Bibliothèque', {'fields': ('est_bibliothecaire', 'slug')}),
    )
    
    def active_borrows_count(self, obj):
        count = obj.get_active_emprunts_count()
        if count > 0:
            return format_html(
                '<span style="color: {};">{}</span>',
                'red' if count >= 3 else 'orange',
                count
            )
        return 0
    active_borrows_count.short_description = 'Emprunts actifs'

# Category Admin
# @admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'books_count', 'slug')
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',)}
    
    def books_count(self, obj):
        return obj.livres.count()
    books_count.short_description = 'Nombre de livres'

# Book Admin
# @admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'isbn', 'total_copies', 'available_copies', 'categories_list', 'date_ajout')
    list_filter = ('categories', 'date_ajout', 'date_publication')
    search_fields = ('titre', 'auteur', 'isbn')
    prepopulated_fields = {'slug': ('isbn',)}
    filter_horizontal = ('categories',)
    readonly_fields = ('date_ajout',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'auteur', 'isbn', 'slug', 'description', 'date_publication')
        }),
        ('Catégorisation', {
            'fields': ('categories',)
        }),
        ('Média', {
            'fields': ('image_couverture',)
        }),
        ('Métadonnées', {
            'fields': ('date_ajout',),
            'classes': ('collapse',)
        }),
    )
    
    def total_copies(self, obj):
        return obj.get_total_exemplaires()
    total_copies.short_description = 'Total exemplaires'
    
    def available_copies(self, obj):
        available = obj.get_exemplaires_disponibles()
        total = obj.get_total_exemplaires()
        color = 'green' if available > 0 else 'red'
        return format_html(
            '<span style="color: {};">{}/{}</span>',
            color, available, total
        )
    available_copies.short_description = 'Disponibles'
    
    def categories_list(self, obj):
        return ", ".join([cat.nom for cat in obj.categories.all()])
    categories_list.short_description = 'Catégories'

# Exemplaire Admin
# @admin.register(Exemplaire)
class ExemplaireAdmin(admin.ModelAdmin):
    list_display = ('livre', 'numero_exemplaire', 'etat', 'status_display', 'current_borrower', 'date_ajout')
    list_filter = ('etat', 'disponible', 'perdu', 'date_ajout')
    search_fields = ('livre__titre', 'numero_exemplaire', 'livre__auteur')
    readonly_fields = ('date_ajout',)
    
    fieldsets = (
        ('Identification', {
            'fields': ('livre', 'numero_exemplaire')
        }),
        ('État', {
            'fields': ('etat', 'disponible', 'perdu', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('date_ajout',),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        if obj.perdu:
            return format_html('<span style="color: red;">Perdu</span>')
        elif not obj.disponible:
            return format_html('<span style="color: orange;">Emprunté</span>')
        else:
            return format_html('<span style="color: green;">Disponible</span>')
    status_display.short_description = 'Statut'
    
    def current_borrower(self, obj):
        try:
            emprunt = obj.emprunt_actuel
            if emprunt.accepter and not emprunt.date_retour_reel:
                return format_html(
                    '<a href="{}">{}</a>',
                    reverse('admin:library_emprunter_change', args=[emprunt.id]),
                    emprunt.utilisateur.username
                )
        except:
            pass
        return "-"
    current_borrower.short_description = 'Emprunté par'

# Main Borrow Admin - This is where librarians manage all borrowing
# @admin.register(Emprunter)
class EmprunterAdmin(admin.ModelAdmin):
    list_display = (
        'utilisateur', 'livre_title', 'exemplaire_info', 'date_demande', 
        'duree_jours', 'status_display', 'date_retour_prevue', 'overdue_days', 'admin_actions'
    )
    list_filter = ('statut', 'accepter', 'date_demande', 'date_retour_prevue')
    search_fields = ('utilisateur__username', 'exemplaire__livre__titre', 'exemplaire__livre__auteur')
    date_hierarchy = 'date_demande'
    ordering = ['-date_demande']
    
    fieldsets = (
        ('Demande d\'emprunt', {
            'fields': ('utilisateur', 'exemplaire', 'duree_jours', 'notes_utilisateur')
        }),
        ('Gestion administrative', {
            'fields': ('accepter', 'statut', 'notes_admin')
        }),
        ('Dates', {
            'fields': ('date_demande', 'date_emprunt', 'date_retour_prevue', 'date_retour_reel'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('date_demande',)
    
    actions = ['approve_borrows', 'reject_borrows', 'mark_returned', 'send_reminder']
    
    def livre_title(self, obj):
        return obj.exemplaire.livre.titre
    livre_title.short_description = 'Livre'
    
    def exemplaire_info(self, obj):
        return f"#{obj.exemplaire.numero_exemplaire}"
    exemplaire_info.short_description = 'Exemplaire'
    
    def status_display(self, obj):
        colors = {
            'en_attente': 'orange',
            'accepte': 'green',
            'refuse': 'red',
            'rendu': 'blue',
            'en_retard': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.statut, 'black'),
            obj.get_statut_display()
        )
    status_display.short_description = 'Statut'
    
    def overdue_days(self, obj):
        if obj.is_overdue():
            days = obj.days_overdue()
            return format_html(
                '<span style="color: red; font-weight: bold;">+{} jours</span>',
                days
            )
        return "-"
    overdue_days.short_description = 'Retard'
    
    def admin_actions(self, obj):
        actions = []
        if obj.statut == 'en_attente':
            actions.append(
                format_html(
                    '<a class="button" href="{}">Approuver</a>',
                    f"{reverse('admin:library_emprunter_change', args=[obj.id])}?approve=1"
                )
            )
        if obj.accepter and not obj.date_retour_reel:
            actions.append(
                format_html(
                    '<a class="button" href="{}">Marquer rendu</a>',
                    f"{reverse('admin:library_emprunter_change', args=[obj.id])}?return=1"
                )
            )
        return format_html(' '.join(actions))
    admin_actions.short_description = 'Actions'
    
    # Custom admin actions
    def approve_borrows(self, request, queryset):
        approved = 0
        for emprunt in queryset.filter(statut='en_attente'):
            if emprunt.utilisateur.can_borrow_more_books() and emprunt.exemplaire.is_available():
                emprunt.accepter = True
                emprunt.save()
                approved += 1
        self.message_user(
            request,
            f"{approved} emprunts approuvés avec succès.",
            messages.SUCCESS
        )
    approve_borrows.short_description = "Approuver les emprunts sélectionnés"
    
    def reject_borrows(self, request, queryset):
        rejected = queryset.filter(statut='en_attente').update(statut='refuse')
        self.message_user(
            request,
            f"{rejected} emprunts refusés.",
            messages.SUCCESS
        )
    reject_borrows.short_description = "Refuser les emprunts sélectionnés"
    
    def mark_returned(self, request, queryset):
        returned = 0
        for emprunt in queryset.filter(accepter=True, date_retour_reel__isnull=True):
            emprunt.date_retour_reel = timezone.now().date()
            emprunt.save()
            returned += 1
        self.message_user(
            request,
            f"{returned} livres marqués comme rendus.",
            messages.SUCCESS
        )
    mark_returned.short_description = "Marquer comme rendus"
    
    def send_reminder(self, request, queryset):
        # This would integrate with email system
        overdue_count = queryset.filter(statut='en_retard').count()
        self.message_user(
            request,
            f"Rappels envoyés pour {overdue_count} emprunts en retard.",
            messages.INFO
        )
    send_reminder.short_description = "Envoyer rappels de retard"

# Reservation Admin
# @admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'livre', 'date_reservation', 'active', 'notifie')
    list_filter = ('active', 'notifie', 'date_reservation')
    search_fields = ('utilisateur__username', 'livre__titre')
    actions = ['notify_users', 'cancel_reservations']
    
    def notify_users(self, request, queryset):
        # This would send notifications to users
        notified = queryset.filter(active=True).update(notifie=True)
        self.message_user(
            request,
            f"{notified} utilisateurs notifiés de la disponibilité.",
            messages.SUCCESS
        )
    notify_users.short_description = "Notifier les utilisateurs"
    
    def cancel_reservations(self, request, queryset):
        cancelled = queryset.update(active=False)
        self.message_user(
            request,
            f"{cancelled} réservations annulées.",
            messages.SUCCESS
        )
    cancel_reservations.short_description = "Annuler les réservations"

# Custom Admin Site Configuration
admin.site.site_header = "Gestion de Bibliothèque"
admin.site.site_title = "Bibliothèque Admin"
admin.site.index_title = "Panneau d'administration"

# Dashboard customization would go in admin.py or custom views
class LibraryAdminMixin:
    """Mixin to add library-specific functionality to admin"""
    
    def get_queryset(self, request):
        """Optimize queries for better performance"""
        qs = super().get_queryset(request)
        if hasattr(qs.model, 'select_related_fields'):
            qs = qs.select_related(*qs.model.select_related_fields)
        if hasattr(qs.model, 'prefetch_related_fields'):
            qs = qs.prefetch_related(*qs.model.prefetch_related_fields)
        return qs