from django.shortcuts import redirect
from functools import wraps

def librarian_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.est_bibliothecaire:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view