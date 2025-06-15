from django.db import models
from django.utils.text import slugify
from accounts.models import Utilisateur
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta

# Category Model
class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=150, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

class Livre(models.Model):
    id = models.AutoField(primary_key=True)
    auteur = models.CharField(max_length=128)
    titre = models.CharField(max_length=128)
    isbn = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    date_publication = models.DateField()
    date_ajout = models.DateTimeField(auto_now_add=True)
    image_couverture = models.ImageField(upload_to='images', null=True, blank=True)
    categories = models.ManyToManyField(Categorie, related_name='livres')
    
    def get_total_exemplaires(self):
        """Get total number of copies (including unavailable ones)"""
        return self.exemplaires_livre.count()
    
    def get_exemplaires_disponibles(self):
        """Get number of available copies"""
        return self.exemplaires_livre.filter(
            disponible=True, 
            perdu=False
        ).count()
    
    def get_max_borrow_days(self):
        """Determine max borrow days based on availability"""
        available_copies = self.get_exemplaires_disponibles()
        total_copies = self.get_total_exemplaires()
        
        if total_copies == 0:
            return 0
        
        # If more than 50% copies available, allow 7 days, otherwise 3 days
        availability_ratio = available_copies / total_copies
        return 7 if availability_ratio > 0.5 else 3
    
    def is_available_for_borrow(self):
        """Check if book has available copies"""
        return self.get_exemplaires_disponibles() > 0
    
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("livre", kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Generate slug from ISBN if not already defined
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

# Copy/Exemplaire Model
class Exemplaire(models.Model):
    ETAT_CHOICES = [
        ('excellent', 'Excellent'),
        ('bon', 'Bon'),
        ('acceptable', 'Acceptable'),
        ('mauvais', 'Mauvais'),
    ]
    
    id = models.AutoField(primary_key=True)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='exemplaires_livre')
    numero_exemplaire = models.CharField(max_length=50)  # Internal tracking number
    disponible = models.BooleanField(default=True)
    perdu = models.BooleanField(default=False)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='excellent')
    date_ajout = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def is_available(self):
        """Check if this copy is available for borrowing"""
        print( self.disponible )
        print( not self.perdu  )
        return self.disponible and not self.perdu 
    
    def __str__(self):
        return f"{self.livre.titre} - Exemplaire #{self.numero_exemplaire}"
    
    class Meta:
        unique_together = ['livre', 'numero_exemplaire']

# Borrow Model
class Emprunter(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('rendu', 'Rendu'),
        ('en_retard', 'En retard'),
    ]
    
    exemplaire = models.OneToOneField(
        Exemplaire, 
        on_delete=models.CASCADE,
        related_name='emprunt_actuel'
    )
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_emprunt = models.DateField(blank=True, null=True)  # When admin approves
    date_retour_prevue = models.DateField(blank=True, null=True)
    date_retour_reel = models.DateField(blank=True, null=True)
    duree_jours = models.IntegerField(default=3)  # 3 to 7 days
    accepter = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    notes_admin = models.TextField(blank=True, null=True)
    notes_utilisateur = models.TextField(blank=True, null=True)
    est_retourne = models.BooleanField(default=False)
    
    def clean(self):
        # Validate user can borrow more books
        if not self.accepter and not self.utilisateur.can_borrow_more_books():
            raise ValidationError("L'utilisateur a déjà atteint la limite de 3 livres empruntés.")
        
        # Validate borrow duration based on book availability
        max_days = self.exemplaire.livre.get_max_borrow_days()
        if self.duree_jours > max_days:
            raise ValidationError(f"La durée maximum d'emprunt pour ce livre est de {max_days} jours.")
        
        # Validate exemplaire is available
        if not self.exemplaire.is_available() and not self.pk:
            raise ValidationError("Cet exemplaire n'est pas disponible.")
    
    def save(self, *args, **kwargs):
        # Set dates when admin accepts the borrow
        if self.accepter and not self.date_emprunt:
            self.date_emprunt = timezone.now().date()
            self.date_retour_prevue = self.date_emprunt + timedelta(days=self.duree_jours)
            self.statut = 'accepte'
            # Mark exemplaire as unavailable
            self.exemplaire.disponible = False
            self.exemplaire.save()
        
        # Update status based on return
        if self.date_retour_reel:
            self.statut = 'rendu'
            # Mark exemplaire as available again
            self.exemplaire.disponible = True
            self.exemplaire.save()
        elif self.accepter and self.date_retour_prevue and timezone.now().date() > self.date_retour_prevue:
            self.statut = 'en_retard'
        
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        """Check if the borrow is overdue"""
        if self.date_retour_prevue and not self.date_retour_reel:
            return timezone.now().date() > self.date_retour_prevue
        return False
    
    def days_overdue(self):
        """Calculate how many days overdue"""
        if self.is_overdue():
            return (timezone.now().date() - self.date_retour_prevue).days
        return 0
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.exemplaire.livre.titre}"
    
    class Meta:
        verbose_name = "Emprunt"
        verbose_name_plural = "Emprunts"
        ordering = ['-date_demande']

# Reservation System (Optional enhancement)
class Reservation(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='reservations')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_reservation = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    notifie = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Réservation: {self.utilisateur.username} - {self.livre.titre}"
    
    class Meta:
        unique_together = ['livre', 'utilisateur']
        ordering = ['date_reservation']



class Notification(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"
    
    class Meta:
        ordering = ['-created_at']



