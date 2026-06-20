from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Логин",
        error_messages={
            "required": "Введите логин.",
            "unique": "Такой логин уже занят.",
        }
    )

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        error_messages={
            "required": "Введите пароль.",
        }
    )

    password2 = forms.CharField(
        label="Повтор пароля",
        widget=forms.PasswordInput,
        error_messages={
            "required": "Повторите пароль.",
        }
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Такой логин уже занят.")

        return username