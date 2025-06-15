from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import register, signup, pagelogin, login_user, logout_user, users_lists, delete_user

urlpatterns = [
    path('register/', register, name='register'),
    path('signup/', signup, name='signup'),
    path('logout_user/', logout_user, name='logout_user'),
    path('users_lists/', users_lists, name='users_lists'),
    path('delete_user/<slug:username>/', delete_user, name='delete_user'),
    path('pagelogin/', pagelogin, name='pagelogin'),
    path('login/', login_user, name='login'),
    
    
    # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),
]