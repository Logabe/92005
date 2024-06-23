from django.contrib.auth.models import User
from django.db.models import QuerySet

from .models import Book, Library

def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None

def related_books(user: User) -> QuerySet:
    user_libraries = Library.objects.filter(members=user)
    related_users = User.objects.filter(memberships__in=user_libraries).distinct()
    return Book.objects.filter(owner__in=related_users)