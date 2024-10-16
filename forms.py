from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from store.models import Review, Customer, ShippingAddress


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form=control'
    }))


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form=control'
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form=control'
    }))

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    firstname = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    lastname = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ('username', 'firstname', 'lastname', 'email', 'password1', 'password2')


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control'
            })
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name..'

            }),

            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your lastname..'
            })
        }



class ShippingForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['address', 'city', 'region', 'phone']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your address...'
            }),

            'city': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Your city...'
            }),

            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your region...'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone num...'
            }),




        }

