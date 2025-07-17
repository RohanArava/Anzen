from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if pwd and confirm and pwd != confirm:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

class TOTPURLForm(forms.Form):
    otp_url = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        label="TOTP URL",
        help_text="Paste the otpauth:// URL here (from QR or manual setup)"
    )

class UnlockForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Your password")
