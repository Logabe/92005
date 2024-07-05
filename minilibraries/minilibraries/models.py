from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class Library(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User, related_name='memberships')

    def __str__(self):
        return self.name

class Book(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    olid = models.CharField(max_length=20)
    isbn = models.CharField(max_length=13)
    title = models.CharField(max_length=200, null=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_returned = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.title

class Request(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return self.user.username + " requests " + self.book.title