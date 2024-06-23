from django.http.response import HttpResponseRedirect
from django.urls import reverse
from functools import wraps
def requires_auth(function):
    @wraps(function)
    def wrapper(request, *args, **kwagrs):
        if request.user.is_authenticated:
            return function(request, *args, **kwagrs)
        else:
            return HttpResponseRedirect(reverse("login"))

    return wrapper