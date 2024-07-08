from datetime import datetime, timedelta
import threading

from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponseForbidden, HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template import Context
from django.template.engine import Engine
from django.core.exceptions import ObjectDoesNotExist
from .models import Library, Book, Request, Invite
from .forms import RegisterBookForm
from .utils import get_or_none, related_books
import requests

def index(request):
    context = {
        'user_count': User.objects.count(),
        'library_count': Library.objects.count(),
        'book_count': Book.objects.count()
    }
    return render(request, "minilibraries/index.html", context)

@login_required
def home(request: HttpRequest):
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
    try:
        book = Book.objects.get(id=book_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("This book does not exist!")

    if related_books(request.user).contains(book):
        req = requests.get(f'http://openlibrary.org/books/{book.olid}.json').json()
        work_id = req["works"][0]["key"]

        work = requests.get(f'http://openlibrary.org{work_id}.json').json()
        desc = work.get("description")

        author_id = work["authors"][0]["author"]["key"]
        author = requests.get(f'http://openlibrary.org{author_id}.json').json()["name"]
        # Sometimes, OL will return a dictionary instead of a string...
        if type(desc) is dict:
            desc = desc.get('value')

        context = {
            "title": book.title,
            "author": author,
            "isbn": book.isbn,
            "owner": book.owner,
            "id": book_id,
            "desc": desc,
            "has_book": book.borrower == request.user,
            "book_request": get_or_none(Request, book_id=book_id, user=request.user),
            "request_count": Request.objects.filter(book=book).exclude(user=request.user).count(),
            "taken_out": book.owner,
            "is_owner": book.owner == request.user,
            "req": req,
            "work": work,
        }
        return render(request, "minilibraries/book.html", context)
    else:
        return HttpResponseForbidden()


def books(request: HttpRequest):
    return books_page(request, 0)

@login_required
@require_GET
def books_page(request: HttpRequest, page: int):
    form = RegisterBookForm()
    start = page * 20
    end = start + 20

    books = related_books(request.user)
    if "search" in request.GET:
        books = books.filter(title__icontains=request.GET["search"])

    match request.GET.get("order"):
        case 'recent':
            books = books.order_by('-date_added')
        case 'old':
            books = books.order_by('date_added')
        case 'AtoZ':
            books = books.order_by('title')
        case 'ZtoA':
            books = books.order_by('-title')
        case 'rand':
            books = books.order_by('?')
        case _:
            pass

    context = {
        "form": form,
        "books": books[start:end],
        "page": page,
        "is_more": end < Book.objects.count()
    }
    return render(request, "minilibraries/books.html", context)

@require_POST
@login_required
def register_book(request: HttpRequest):
    isbn = request.POST["isbn"]

    try:
        r = requests.get(f'http://openlibrary.org/api/volumes/brief/isbn/{isbn}.json')
        if len(r.text) <= 2:
            return HttpResponseServerError("Couldn't load data for this book. This might be because the ISBN you inputted is incorrect, or it might be that Open Library doesn't have any records of your book.")
        book_data = r.json()["records"][list(r.json()["records"])[0]]
        olid = book_data["olids"][0]
        title = book_data["data"]["title"]
        date = datetime.now()

        book = Book(owner = request.user, olid=olid, title=title, isbn = isbn, date_added=date)
        book.save()
        return HttpResponse("Registered "+ book.title)
    except Exception as e:
        return HttpResponseServerError("Internal error: Could not register book")


@require_POST
@login_required
def delete_book(request: HttpRequest, book_id):
    book = Book.objects.get(id=book_id)
    if book.owner.pk == request.user.id:
        book.delete()
        return HttpResponse("Delete successful")
    else:
        return HttpResponseForbidden()

email_template = Engine.get_default().get_template(template_name="minilibraries/email.txt")
alternative_email = Engine.get_default().get_template(template_name="minilibraries/additional_email.txt")

@require_POST
@login_required
def request_book(request: HttpRequest, book_id):
    def email(user, book: Book):
        borrower = book.borrower.get_full_name() if book.borrower else Request.objects.filter(book=book).latest('-date').user.get_full_name()
        print(borrower)
        context = Context({"user": user, "book": book, "borrower": borrower})
        template = alternative_email if book.borrower or Request.objects.filter(book=book).count() >= 1 else email_template
        book.owner.email_user("Request for " + book.title, template.render(context=context), "logangbentley@gmail.com")

    book = Book.objects.get(id=book_id)
    if related_books(request.user).contains(book):
        if Request.objects.filter(user=request.user).count() + Book.objects.filter(borrower=request.user).count() <= settings.BORROW_LIMIT:
            if get_or_none(Request, user=request.user, book=book) or book.borrower == request.user:
                return HttpResponseForbidden("Already requested/borrowed")
            else:
                Request(user = request.user, book = book, date=datetime.now()).save()
                email_thread = threading.Thread(target=email, name="Email Thread", args=(request.user, book))
                email_thread.start()
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
    if Request.objects.filter(book=book).latest('-date') != book_request:
        return HttpResponseForbidden("Not the first request ")

    if request.user.id == book.owner.id:
        book.borrower = request.user
        book.save()
        book_request.delete()
        return HttpResponse("does anyone even read these")
    else:
        return HttpResponseForbidden("Not the owner")

@require_POST
@login_required
def cancel_request(request: HttpRequest):
    book_request = Request.objects.get(pk=request.POST["request_id"])
    if book_request.user == request.user:
        book_request.delete()
        return HttpResponse("Canceled successfully")
    return HttpResponseForbidden("Request doesn't exist")

@login_required()
def join(request: HttpRequest, code):
    try:
        invite = Invite.objects.get(pk=code)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Invitation does not exist!")

    if request.method == "POST":
        invite.library.members.add(request.user)
        invite.library.save()
        return HttpResponseRedirect("/home")
    else:
        return render(request, "minilibraries/join.html", {"invite": invite})