# In appBibliotheque/utils.py
from .models import Notification

def send_notification(user, message, link=None):
    """
    Send a notification to a user
    """
    Notification.objects.create(
        user=user,
        message=message,
        link=link
    )