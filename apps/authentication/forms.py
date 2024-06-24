from django import forms


class LoginForm(forms.Form):
    
    username = forms.CharField(
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'id': 'username',
            'maxlength': '40',
            'required': 'required'
        })
    )
    
    password = forms.CharField(
        max_length=40,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'id': 'password',
            'maxlength': '40',
            'required': 'required'
        })
    )
