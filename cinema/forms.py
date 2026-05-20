from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Rating, Newsletter


class RatingForm(forms.ModelForm):
    score = forms.ChoiceField(
        choices=[(i, f'{i} ⭐') for i in range(1, 11)],
        label='Оцінка',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Ваш коментар (необов\'язково)...'
            }),
        }
        labels = {'comment': 'Коментар'}


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your@email.com'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше ім\'я'
            }),
        }
        labels = {
            'email': 'Email адреса',
            'name': 'Ім\'я',
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ім\'я'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Прізвище'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Логін'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Повторіть пароль'})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Логін'})
        self.fields['password'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Пароль'})


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label='Email адреса',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'})
    )


class PasswordResetConfirmForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label='Код з листа',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '123456'})
    )
    new_password = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Новий пароль'})
    )
    new_password2 = forms.CharField(
        label='Повторіть пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Повторіть пароль'})
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Паролі не співпадають.')
        return cleaned
