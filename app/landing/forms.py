from django import forms
from .models import Contacto
from django_recaptcha.widgets import ReCaptchaV3
from django_recaptcha.fields import ReCaptchaField
from typing import Any


class FormularioContacto(forms.ModelForm):
    captcha: ReCaptchaField = ReCaptchaField(widget=ReCaptchaV3)
    # Campo honeypot: invisible para humanos, los bots lo rellenan
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Contacto
        fields: list[str] = ['nombre', 'email', 'asunto', 'mensaje', 'captcha']

        widgets: dict[str, Any] = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Tu email'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu mensaje...', 'rows': 4}),
        }

    def clean_website(self) -> str:
        """Honeypot: si un bot rellena este campo oculto, rechazamos el envío."""
        value = self.cleaned_data.get('website', '')
        if value:
            raise forms.ValidationError("Bot detectado.")
        return value

    def clean_nombre(self) -> str:
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

    def clean_asunto(self) -> str:
        asunto = self.cleaned_data.get('asunto', '').strip()
        if len(asunto) < 3:
            raise forms.ValidationError("El asunto debe tener al menos 3 caracteres.")
        return asunto

    def clean_mensaje(self) -> str:
        mensaje = self.cleaned_data.get('mensaje', '').strip()
        if len(mensaje) < 10:
            raise forms.ValidationError("El mensaje debe tener al menos 10 caracteres.")
        return mensaje