from functools import wraps
from flask import abort
from flask_login import current_user
from movieapp.models import UserRole


def login_user_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        return f(*args, **kwargs)

    return decorated_func


def anonymous_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            abort(403)
        return f(*args, **kwargs)

    return decorated_func


def user_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)

        if current_user.role != UserRole.USER:
            abort(403)

        return f(*args, **kwargs)

    return decorated_func


def staff_or_admin_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)

        if current_user.role not in [UserRole.STAFF, UserRole.ADMIN]:
            abort(403)

        return f(*args, **kwargs)

    return decorated_func
