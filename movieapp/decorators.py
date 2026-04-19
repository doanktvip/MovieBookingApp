from functools import wraps
from flask import redirect
from flask_login import current_user

from movieapp.models import UserRole


def login_user_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_func


def anonymous_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_func


def staff_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.STAFF:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_func


def user_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.USER:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_func


def admin_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_func
