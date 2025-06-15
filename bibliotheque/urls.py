from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    # Include apps URLs
    path('', include('appBibliotheque.urls')),
    path('accounts/', include('accounts.urls')),
    path('admins/', include('superAcount.urls')),
    
    # Add any other global URLs here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# from django.contrib import admin
# from django.urls import path, include
# from appBibliotheque.views import *
# from appBibliotheque.views import emprunter_exemplaire,liste_livres,page_ajout,supprimer_exemplaire,detailLivre,dashboard
# # from appBibliotheque.views import categorie_math,categorie_Roman,categorie_Physique,categorie_Sport,categorie_Social,categorie_culture
# from accounts.views import register,signup,pagelogin,login_user,logout_user,users_lists,delete_user
# from django.contrib.auth import views as auth_views
# from django.conf.urls.static import static
# from django.conf import settings
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path("__reload__/", include("django_browser_reload.urls")),
#     path('',home,name="home"),
#     path('register/',register,name='register'),
#     path('genre/<str:genre>', filterLivre, name='filterLivre'),
#     path('page_UnLivre/',page_UnLivre,name='page_UnLivre'),
#     path('signup/',signup,name='signup'),
#     path('logout_user',logout_user,name='logout_user'),
#     path('users_lists/',users_lists,name='users_lists'),
#     path('delete_user/<slug:username>/',delete_user,name='delete_user'),
#     path('page_ajout/',page_ajout,name='page_ajout'),
#     path('pagelogin/',pagelogin,name='pagelogin'),
#     path('rechercher_livre/',rechercher_livre,name='rechercher_livre'),
#     path('ajouter_livre/',ajouter_livre,name='ajouter_livre'),
#     path('edit_livre/<int:id>',edit_livre,name='edit_livre'),
#     path('liste_livres/',liste_livres,name='liste_livres'),
#     path('supprimer_exemplaire/<int:id>',supprimer_exemplaire,name='supprimer_exemplaire'),
#     path('detail_livre/<slug:slug>',detail_livre,name='detail_livre'),
#     path('ajouter_exemplaire/<int:id>',ajouter_exemplaire,name='ajouter_exemplaire'),
#     path('detailLivre/<int:id>',detailLivre,name='detailLivre'),
#     # path('livre/<slug:slug>/emprunter_exemplaire',emprunter_exemplaire,name='emprunter_exemplaire'),
#     path('login/',login_user,name='login'),
#     path('dashboard/',dashboard,name="dashboard"),
#     path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
#     path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
#     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
#     path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
#     path('about/',about_us, name='about'),
#     path('contact/',contact_us, name='contact'),
#     path('emprunter/<slug:slug>/', emprunter_exemplaire, name='emprunter_exemplaire'),
#     path('profile/', profile, name='profile'),

# ] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
