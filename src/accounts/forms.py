from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from common.forms import style_fields


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Tên đăng nhập"
        self.fields["password"].label = "Mật khẩu"
        style_fields(self)


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Tên đăng nhập"
        self.fields["username"].help_text = "Tối đa 150 ký tự. Dùng chữ, số hoặc @ . + - _"
        self.fields["password1"].label = "Mật khẩu"
        self.fields[
            "password1"
        ].help_text = "Ít nhất 8 ký tự; tránh mật khẩu phổ biến hoặc chỉ gồm số."
        self.fields["password2"].label = "Nhập lại mật khẩu"
        self.fields["password2"].help_text = "Nhập lại mật khẩu ở trên để xác nhận."
        style_fields(self)
