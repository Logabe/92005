from datetime import datetime, timedelta

from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .models import Library, Book, Request
from .forms import RegisterBookForm
from .utils import get_or_none, related_books
import requests
import json
import asyncio
from asgiref.sync import sync_to_async

def index(request):
    context = {
        'user_count': User.objects.count(),
        'library_count': Library.objects.count(),
        'book_count': Book.objects.count()
    }
    return render(request, "minilibraries/index.html", context)

@login_required
def home(request: HttpRequest):
    user_libraries = Library.objects.filter(members=request.user)
    five_days = datetime.now() - timedelta(days=3)
    context = {
        "name": request.user.username,
        "libraries": request.user.memberships.all(),
        "requested": Request.objects.filter(book__owner=request.user),
        "taken_out": Book.objects.filter(borrower=request.user),
        "taken_out_count": Book.objects.filter(borrower=request.user).count(),
        "user_registered": Book.objects.filter(owner=request.user).count(),
        "newly_added": related_books(request.user).order_by('date_added')[:15],
        "new_returns": related_books(request.user).filter(last_returned__gte=five_days).order_by('-last_returned')[:15],
    }
    return render(request, "minilibraries/home.html", context)

@login_required
def book(request: HttpRequest, book_id):
    book = Book.objects.get(id=book_id)
    if related_books(request.user).contains(book):
        req = requests.get(f'http://openlibrary.org/books/{book.olid}.json').json()
        work_id = req["works"][0]["key"]

        work = requests.get(f'http://openlibrary.org{work_id}.json').json()
        desc = work.get("description")
        # Sometimes, OL will return a dictionary instead of a string...
        if type(desc) is dict:
            desc = desc.get('value')

        context = {
            "title": book.title,
            "isbn": book.isbn,
            "owner": book.owner,
            "id": book_id,
            "desc": desc,
            "has_book": book.borrower == request.user,
            "request": get_or_none(Request, book_id=book_id, user=request.user),
            "is_owner": book.owner == request.user
        }
        return render(request, "minilibraries/book.html", context)
    else:
        return HttpResponseForbidden()

@login_required
@require_GET
def books(request: HttpRequest):
    form = RegisterBookForm()
    #
    books = related_books(request.user)[:20]
    context = {
        "form": form,
        "books": books
    }
    return render(request, "minilibraries/books.html", context)

@require_POST
@login_required
def register_book(request: HttpRequest):
    isbn = request.POST["isbn"]
    r = requests.get(f'http://openlibrary.org/api/volumes/brief/isbn/{isbn}.json')
    book_data = r.json()["records"][list(r.json()["records"])[0]]
    olid = book_data["olids"][0]
    title = book_data["data"]["title"]
    date = datetime.now()

    book = Book(owner = request.user, olid=olid, title=title, isbn = isbn, date_added=date)
    book.save()
    return HttpResponseRedirect("/books")

@require_POST
@login_required
def delete_book(request: HttpRequest, book_id):
    book = Book.objects.get(id=book_id)
    if book.owner.pk == request.user.id:
        book.delete()
        return HttpResponse("Delete successful")
    else:
        return HttpResponseForbidden()

@require_POST
@login_required
def request_book(request: HttpRequest, book_id):
    def email(user, book):
        message = f"""Hello {book.owner.first_name},
        {user.get_full_name()} ({user.get_username()}) has requested your copy of {book.title}
        Their email is: {user.email}"""

        book.owner.email_user("Request for " + book.title, message, "logangbentley@gmail.com")

    book = Book.objects.get(id=book_id)
    if related_books(request.user).contains(book):
        if Request.objects.filter(user=request.user).count() + Book.objects.filter(borrower=request.user).count() <= settings.BORROW_LIMIT:
            if get_or_none(Request, user=request.user, book=book) or book.borrower == request.user:
                return HttpResponseForbidden("Already requested/borrowed")
            else:
                Request(user = request.user, book = book, date=datetime.now()).save()
                asyncio.run(asyncio.coroutine(email(request.user, book)))
                return HttpResponse("Request successful")
        else:
            return HttpResponseForbidden(f"Too many books/requests out (limit: {settings.BORROW_LIMIT})")
    else:
        return HttpResponseForbidden()


@require_POST
@login_required
def return_book(request: HttpRequest, book_id):
    book = Book.objects.get(id=book_id)
    if book.borrower.pk == request.user.id:
        book.borrower = None
        book.last_returned = datetime.now()
        book.save()
        return HttpResponse("Return successful")
    else:
        return HttpResponseForbidden()

@require_POST
@login_required
def fulfill_request(request: HttpRequest):
    book_request = Request.objects.get(pk=request.POST["request_id"])
    book = book_request.book
    if request.user.id == book.owner.id:
        book.borrower = request.user
        book.save()
        book_request.delete()
        return HttpResponse("does anyone even read these")
    else:
        return HttpResponseForbidden()

@require_POST
@login_required
def cancel_request(request: HttpRequest):
    book_request = Request.objects.get(pk=request.POST["request_id"])
    if book_request.user == request.user:
        book_request.delete()
        return HttpResponse("Canceled successfully")
    return HttpResponseForbidden("Request doesn't exist")
