from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout, forms
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data.get("username")).exists():
                return HttpResponseForbidden("Username already taken!")

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
        form = forms.AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get("username"), password=form.cleaned_data.get("password"))
            if user is not None:
                dj_login(request, user)
                next = request.POST.get('next', default='')
                if next == "":
                    return HttpResponseRedirect("/home")
                else:
                    return HttpResponseRedirect(next)

        return HttpResponseForbidden("Could not log you in")
    else:
        form = forms.AuthenticationForm()
        return render(request, "auth/login.html", {"form": form})

def logout(request: HttpRequest):
    dj_logout(request)
    return HttpResponseRedirect("/")