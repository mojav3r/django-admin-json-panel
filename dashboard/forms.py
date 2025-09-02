from django import forms


class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput({'placeholder': '  ', 'dir': 'auto',
                                'class': 'floating-input form-control'}), min_length=1)
    password = forms.CharField(widget=forms.PasswordInput({'placeholder': '  ', 'dir': 'auto',
                                                           'class': 'floating-input form-control'}))


class JsonUploadForm(forms.Form):
    author = forms.CharField(
        widget=forms.TextInput({'placeholder': 'Author name', 'dir': 'auto',
                                'class': 'form-control'}), min_length=1)
    upload = forms.FileField(widget=forms.FileInput({'class': 'custom-file-input', 'id': 'inputGroupFile01'}))
