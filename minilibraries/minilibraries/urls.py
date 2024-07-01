from django.urls import path
from django.conf.urls import handler404
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("books", views.books, name="books"),
    path("books/<int:page>", views.books_page, name="books"),
    path("book/add", views.register_book, name="add_book"),
    path("book/<int:book_id>", views.book, name="book"),
    path("book/<int:book_id>/delete", views.delete_book, name="delete_book"),
    path("book/<int:book_id>/request", views.request_book, name="request_book"),
    path("book/<int:book_id>/return", views.return_book, name="return_book"),
    path("fulfill_request", views.fulfill_request, name="fulfill_request"),
    path("cancel_request", views.cancel_request, name="cancel_request")
]