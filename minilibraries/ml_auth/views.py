from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data.get("username"), form.cleaned_data.get("email"), form.cleaned_data.get("password"))
            user.first_name = form.cleaned_data.get("firstname")
            user.last_name = form.cleaned_data.get("lastname")
            if user is not None:
                user.save()
                dj_login(request, user)
                return HttpResponseRedirect("/home")

        return HttpResponseForbidden("Could not register user")


    form = RegisterForm()
    return render(request, "auth/register.html", {"form": form})

def login(request: HttpRequest):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get("username"), password=form.cleaned_data.get("password"))
            if user is not None:
                dj_login(request, user)
            return HttpResponseRedirect("/home")
        else:
            return HttpResponseForbidden("Could not log you in")


    form = LoginForm()
    return render(request, "auth/login.html", {"form": form})

def logout(request: HttpRequest):
    dj_logout(request)
    return HttpResponseRedirect("/")