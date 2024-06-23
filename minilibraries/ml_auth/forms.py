from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    firstname = forms.CharField(label="First Name", max_length=20, required=False)
    lastname = forms.CharField(label="Last Name", max_length=20, required=False)
    username = forms.CharField(label="Username", max_length=32)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
