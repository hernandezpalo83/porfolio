from django import forms
from .models import Contacto
from django_recaptcha.widgets import ReCaptchaV3
from django_recaptcha.fields import ReCaptchaField
from typing import Any

class FormularioContacto(forms.ModelForm):
    # El widget invisible de Google
    captcha: ReCaptchaField = ReCaptchaField(widget=ReCaptchaV3)
    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = Contacto
        # Solo pedimos los campos que el usuario debe rellenar
        fields: list[str] = ['nombre', 'email', 'asunto', 'mensaje', 'captcha']
        
        widgets: dict[str, Any] = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Tu email'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu mensaje...', 'rows': 4}),
        }