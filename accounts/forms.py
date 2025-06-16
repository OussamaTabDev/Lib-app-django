from django import forms
from .models import Utilisateur

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        labels = {
            'username': "Nom d'utilisateur",
            'email': 'Adresse e-mail',
            'first_name': 'Prénom',
            'last_name': 'Nom de famille',
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
