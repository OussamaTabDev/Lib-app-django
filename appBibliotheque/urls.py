from django.urls import path
from .views import (
    clear_all_notifications, home, filterLivre, mark_notification_as_read, page_UnLivre, rechercher_livre, 
    ajouter_livre, edit_livre, liste_livres, supprimer_exemplaire,
    detail_livre, ajouter_exemplaire, detailLivre, dashboard,
    about_us, contact_us, emprunter_exemplaire, page_ajout,profile, view_all_notifications, edit_profile,
    return_book
)

urlpatterns = [
    path('', home, name="home"),
    path('genre/<str:genre>/', filterLivre, name='filterLivre'),
    path('page_UnLivre/', page_UnLivre, name='page_UnLivre'),
    path('page_ajout/', page_ajout, name='page_ajout'),
    path('rechercher_livre/', rechercher_livre, name='rechercher_livre'),
    path('ajouter_livre/', ajouter_livre, name='ajouter_livre'),
    path('edit_livre/<int:id>/', edit_livre, name='edit_livre'),
    path('liste_livres/', liste_livres, name='liste_livres'),
    path('supprimer_exemplaire/<int:id>/', supprimer_exemplaire, name='supprimer_exemplaire'),
    path('detail_livre/<slug:slug>/', detail_livre, name='detail_livre'),
    path('ajouter_exemplaire/<int:id>/', ajouter_exemplaire, name='ajouter_exemplaire'),
    path('detailLivre/<int:id>/', detailLivre, name='detailLivre'),
    path('dashboard/', dashboard, name="dashboard"),
    path('about/', about_us, name='about'),
    path('contact/', contact_us, name='contact'),
    path('emprunter/<slug:slug>/', emprunter_exemplaire, name='emprunter_exemplaire'),
    path('profile/', profile, name='profile'),
    path('notifications/', view_all_notifications, name='view_all_notifications'),
    path('notifications/mark-read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_read'),
    path('notifications/clear-all/', clear_all_notifications, name='clear_all_notifications'),
    path('profile/edit-profile/', edit_profile, name='edit_profile'),
    path('return_book/<int:emprunt_id>/', return_book, name='return_book'),
    # path('/add', addnewuser, name='add_user'),

]