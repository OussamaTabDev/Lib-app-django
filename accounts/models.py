from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import re

# Create your models here.
# User Model
class Utilisateur(AbstractUser):
    est_bibliothecaire = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Generate slug from username if empty
        if not self.slug:
            self.slug = slugify(self.username)
        
        # Validate password only for new users
        if not self.pk or self._state.adding:
            self.clean_password()
            
        super().save(*args, **kwargs)

    def clean_password(self):
        password = self.password
        
        # Skip validation if password is already hashed (starts with algorithm identifier)
        if password.startswith('pbkdf2_') or password.startswith('argon2') or password.startswith('bcrypt'):
            return

        # Validate password length
        if len(password) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

        # Validate presence of at least one digit
        if not any(char.isdigit() for char in password):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")

        # Validate presence of at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")

        # Validate presence of at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")

        # Validate presence of at least one special character
        if not re.search(r"[!@#$%^&*()_+=\[\]{};:.,<>?|\\]", password):
            raise ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")

    def get_active_emprunts_count(self):
        """Get number of currently active borrows for this user"""
        return self.emprunter_set.filter(
            statut ="accepte",
            accepter=True,
            date_retour_reel__isnull=True
        ).count()
    
    def can_borrow_more_books(self):
        """Check if user can borrow more books (max 3)"""
        
        return self.get_active_emprunts_count() < 3