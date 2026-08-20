from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)
        labels = {'email': 'メールアドレス'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード(確認)'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に登録されています。')
        return email


class LoginForm(AuthenticationForm):
    # AuthenticationFormは内部的にフィールド名'username'を前提にclean()等を実装しているため、
    # 名前はusernameのまま型・ラベルだけメールアドレス向けに差し替える。
    username = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )
    password = forms.CharField(
        label='パスワード',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': 'メールアドレスまたはパスワードが正しくありません。',
        'inactive': 'このアカウントは無効化されています。',
    }
