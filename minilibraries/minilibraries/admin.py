from django.contrib import admin

from .models import Book, Library, Request, Invite

class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "borrower", "owner"]
    list_filter = ["date_added", "last_returned"]
    search_fields = ["title"]

class RequestAdmin(admin.ModelAdmin):
    list_display = ["book", "user", "date"]

admin.site.register(Book, BookAdmin)
admin.site.register(Library)
admin.site.register(Request, RequestAdmin)
admin.site.register(Invite)