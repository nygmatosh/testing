from django import forms
from captcha.fields import CaptchaField

class SendCommentForm(forms.Form):
    username = forms.CharField(label='', max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(label='', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}))
    home_page = forms.URLField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home page'}))
    captcha = CaptchaField()
    comment = forms.CharField(
        label="Комментарий",
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-sm w-100',
            'rows': 5,
            'cols': 40,
            'placeholder': 'Введите текст комментария...',
            'v-model': 'message_body'
        })
    )
    file = forms.FileField(
        label="Прикрепить файл",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control form-control-sm w-100',
            'accept': ".txt,.png,.jpg,.jpeg,.gif"
        })
    )