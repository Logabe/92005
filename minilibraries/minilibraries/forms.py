from django import forms

class RegisterBookForm(forms.Form):
    isbn = forms.CharField(label="ISBN", max_length=13, required=True)