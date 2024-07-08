from django import forms

class RegisterBookForm(forms.Form):
    isbn = forms.CharField(label="ISBN", required=True)