from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
# from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from .models import Categories, BookFiles


class LoginForm(forms.Form):
    login = forms.CharField(label="Логін", widget=forms.TextInput(

        attrs={
            'class': 'form-control'
        }
    ))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(

        attrs={

            'class': 'form-control'
        }
    ))

    def clean(self):
        username = self.cleaned_data.get('login')
        password = self.cleaned_data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Ви не зареєрестровані в системі")

        if not user.check_password(password):
            raise forms.ValidationError("Неправильний пароль")

        return super(LoginForm, self).clean()


class RegistrationForm(forms.Form):
    username = forms.CharField(label="Логін", widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    name = forms.CharField(label="Ім'я", widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    first_name = forms.CharField(label="Прізвище", widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    last_name = forms.CharField(label="По батькові", widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    email = forms.CharField(label='Емейл', widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(
        attrs={
            'class': 'form-control'
        }
    ))
    password2 = forms.CharField(label="Пароль(Повторно)", widget=forms.PasswordInput(
        attrs={
            'class': 'form-control'
        }
    ))

    def clean(self):
        name = self.cleaned_data.get('name')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        username = self.cleaned_data['username']
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError("Паролі не збігаються")
        try:
            user = User(username=username, password=password1)
        except IntegrityError:
            raise forms.ValidationError("Цей нікнейм вже зайнятий, придумайте інший")
        return super(RegistrationForm, self).clean()


class AddBookForm(forms.Form):
    title = forms.CharField(label="Назва книги", widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    author = forms.CharField(label="Автор книги", widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    translator = forms.CharField(label="Перекладач книги", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    series = forms.CharField(label="Серія", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    countOfPages = forms.IntegerField(label="Кількість сторінок", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    language = forms.CharField(label="Мова книги", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    edition = forms.CharField(label="Видання книги", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))

    description = forms.CharField(label="Опис книги", widget=forms.Textarea(
        attrs={
            'class': 'form-control'
        }
    ))
    image = forms.ImageField(label="Обнладинка книги", required=False, widget=forms.FileInput(
        attrs={
            'class': 'form-control'
        }
    ))

    isPublic = forms.BooleanField(label='Чи книга публічна', required=False, widget=forms.CheckboxInput(
        attrs={
            'class': 'form-check-input m-0 mt-2 ml-1'
        }
    ))


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = BookFiles
        fields = ['file']


class SetCategoryForm(forms.Form):
    category = forms.ModelChoiceField(label='Виберіть категорію', required=False,queryset=Categories.objects.all(),
                                             widget=forms.Select(
                                                 attrs={
                                                     'class': 'form-control selectpicker',
                                                     'data-live-search': "true"
                                                 }
                                             ))
    name = forms.CharField(label=_("Назва категорії"), required=False,widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))

    parent_category = forms.ModelChoiceField(label='Виберіть батьківську категорію',required=False, queryset=Categories.objects.all(),
                                             widget=forms.Select(
                                                 attrs={
                                                     'class': 'form-control selectpicker',
                                                     'data-live-search': "true"
                                                 }
                                             ))
    def clean(self):
        category = self.cleaned_data.get('category')
        category_name = self.cleaned_data.get('name')
        parent_category = self.cleaned_data.get('parent_category')
        if category:
            return super(SetCategoryForm, self).clean()
        elif category_name or category_name and parent_category:
            try:
                category = Categories.objects.create(name=category_name, parent=parent_category)
                category.delete()
                return super(SetCategoryForm, self).clean()
            except Exception:
                raise forms.ValidationError('Категорія з такою назвою вже існує')

        elif parent_category:
            raise forms.ValidationError('Введіть назву категорії')
        else:
            raise forms.ValidationError("Ви маєте заповнити хоча б одне поле")




class ReasonForm(forms.Form):
    reason = forms.CharField(label="Повідомлення", widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'rows': 5
        }
    ))


class SearchBookForm(forms.Form):
    title = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть назву книги"
        }
    ))
    author = forms.CharField(label="", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть автора книги"
        }
    ))
    CHOICES = ((i.name, i.name) for i in Categories.objects.all())
    category = forms.ChoiceField(label='', choices=CHOICES, widget=forms.Select(
        attrs={
            'class': 'form-control selectpicker',
            'data-live-search': "true"
        }
    ))
    CHOICES = (("так", "так"), ("ні", "ні"), ("усі", "усі"))
    is_public = forms.ChoiceField(label='Виберіть категоріюю книги', choices=CHOICES, widget=forms.Select(
        attrs={
            'class': 'form-control selectpicker',
            'data-live-search': "true"
        }
    ))


class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(label="", required=False, widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть пароль"
        }
    ))
    password2 = forms.CharField(label="", required=False, widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть пароль(повторно)"
        }
    ))


class ChangeUserDataForm(forms.Form):
    first_name = forms.CharField(label="Ім'я", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть своє ім'я"
        }
    ))
    name = forms.CharField(label="Прізвище", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть своє прізвище"
        }
    ))
    last_name = forms.CharField(label="Побатькові", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть своє побатькові"
        }
    ))
    username = forms.CharField(label="логін", required=False, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть введіть свій логін"
        }
    ))
    email = forms.CharField(label="Емейл", required=False, widget=forms.EmailInput(
        attrs={
            'class': 'form-control',
            'placeholder': "Введіть свій емейл"
        }
    ))


class CommentForm(forms.Form):
    comment_text = forms.CharField(label="Текст коментаря", widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'rows': 5
        }
    ))
