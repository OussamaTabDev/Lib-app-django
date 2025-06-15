from django.urls import path, include
from django.contrib import admin
from . import views



# Admin management URLs
# admin_patterns = [
#     # path('dashboard/', views.library_dashboard, name='library_dashboard'),
#     path('requests/', views.manage_borrow_requests, name='manage_borrow_requests'),
#     path('active-borrows/', views.active_borrows, name='active_borrows'),
#     path('books/', views.book_management, name='book_management'),
#     path('reports/', views.reports, name='reports'),
#     path('user/<int:user_id>/history/', views.user_borrowing_history, name='user_history'),
#     path('send-reminders/', views.send_overdue_reminders, name='send_reminders'),
    
#     # API endpoints
#     path('api/book/<int:book_id>/availability/', views.api_book_availability, name='api_book_availability'),
#     path('api/user/<int:user_id>/can-borrow/', views.api_user_can_borrow, name='api_user_can_borrow'),
# ]

urlpatterns = [
    path('dashboard/', views.library_dashboard, name='library_dashboard'),
    path('requests/', views.manage_borrow_requests, name='manage_borrow_requests'),
    path('active-borrows/', views.active_borrows, name='active_borrows'),
    path('books/', views.book_management, name='book_management'),
    path('reports/', views.reports, name='reports'),
    path('user/<int:user_id>/history/', views.user_borrowing_history, name='user_history'),
    path('send-reminders/', views.send_overdue_reminders, name='send_reminders'),
    path('api/book/<int:book_id>/availability/', views.api_book_availability, name='api_book_availability'),
    path('api/user/<int:user_id>/can-borrow/', views.api_user_can_borrow, name='api_user_can_borrow'),

    # New URLs
    path('users/', views.user_management, name='user_management'),
    path('books/<int:book_id>/details/', views.book_details, name='book_details'),
    path('empruntes/', views.empruntes_page, name='empruntes_page'),

    # Book management URLs
    path('books/add/', views.add_book, name='add_book'),
    path('books/edit/<int:id>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:id>/', views.delete_book, name='delete_book'),
    ]