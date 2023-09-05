from django import forms

class LoginForms(forms.Form):
    nome_login=forms.CharField(
        required=True,
        max_length=100,
        widget = forms.TextInput(
        attrs={
            "class": "form-control form-control-user",
            "placeholder": "Usuário"
          }
        )
    )
    senha=forms.CharField(
        required=True,
        max_length=70,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Senha"
            }
        )
    )