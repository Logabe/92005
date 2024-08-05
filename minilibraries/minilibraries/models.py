from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Library - A collection of users that can share books with eachother
class Library(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User, related_name='memberships')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "libraries"


# A book
class Book(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner') # The user who owns the book
    olid = models.CharField(max_length=20) # The book's Open Library edition ID
    isbn = models.CharField(max_length=13) # The book's ISBN
    title = models.CharField(max_length=200, null=True) # The book's title (can be null?)
    borrower = models.ForeignKey(User, on_delete=models.PROTECT, null=True, default=None, blank=True) # The book who is currently borrowing the book
    date_added = models.DateTimeField(auto_now_add=True) # The date the book was registered - will be set automatically
    last_returned = models.DateTimeField(blank=True, null=True) # The time the book was last returned

    def __str__(self):
        return self.title


# A request for a book
class Request(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE) # The book in question
    user = models.ForeignKey(User, on_delete=models.CASCADE) # The user who requested the book
    date = models.DateTimeField()                            # The time the book was requested

    def __str__(self):
        return self.user.username + " requests " + self.book.title


# An invitation to a library
class Invite(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE) # The library in question
    key = models.SlugField(max_length=30, primary_key=True)        # (should be a different type)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)    # The user who created the invitation - if this user deletes their account, the invitation will disappear

    def __str__(self):
        return self.key