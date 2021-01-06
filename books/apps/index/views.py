from django.forms.utils import ErrorList
from django.shortcuts import render
from django.views import View
from .forms import *
from django.contrib.auth.models import auth
from django.http import JsonResponse
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .utils import *
from .DataQuery import DataQuery
import json


class HomeView(View):

    def get(self, request, *args, **kwargs):
        print(request.user)
        books = DataQuery.get_all_public_and_users_books(request.user.id)
        form = SearchBookForm(request.POST or None)
        return render(request, 'home.html',
                      {'books': json.dumps(books), "categories": Categories.objects.filter(level=0),
                       "form": form})

    def post(self, request, *args, **kwargs):
        books = DataQuery.get_all_public_and_users_books(request.user.id)
        form = SearchBookForm(request.POST)
        if form.is_valid():
            return get_data_from_search_form(form)
        return render(request, 'home.html', {'books': books, "categories": Categories.objects.filter(level=0),
                                             "form": form})


class CategoryView(View):

    def get(self, request, *args, **kwargs):
        form = SearchBookForm(request.POST or None)
        data = DataQuery.get_category_books_and_children_categories(request.user.id, kwargs['category_id'])

        return render(request, 'category.html', {"books": json.dumps(data['booksFromCategory']), "category": data['category'],
                                                 "categories": data['childrenCategories'], "form": form})

    def post(self, request, *args, **kwargs):
        form = SearchBookForm(request.POST)
        data = DataQuery.get_category_books_and_children_categories(request.user.id, kwargs['category_id'])
        if form.is_valid():
            return get_data_from_search_form(form)
        return render(request, 'category.html', {"books": json.dumps(data['booksFromCategory']), "category": data['category'],
                                                 "categories": data['childrenCategories'], "form": form})


class MyBooks(View):

    def get(self, request, *args, **kwargs):
        books = DataQuery.get_my_books(request.user.id)
        form = SearchBookForm(request.POST or None)
        return render(request, 'my_books.html',
                      {"books": json.dumps(books), "form": form, "categories": Categories.objects.filter(level=0)})

    def post(self, request, *args, **kwargs):
        form = SearchBookForm(request.POST or None)
        if form.is_valid():
            books = search_in_my_books(form, request.user)
        return render(request, 'my_books.html',
                      {"books": json.dumps(books), "form": form, "categories": Categories.objects.filter(level=0)})


class LoginView(View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        return render(request, 'login.html', {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['login'], password=form.cleaned_data['password'])
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect(reverse("index:my_books", args=()))

        return render(request, 'login.html', {"form": form})


class RegisterView(View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        return render(request, 'register.html', {"form": form})

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                            password=form.cleaned_data['password1'],
                                            first_name=form.cleaned_data['first_name'],
                                            last_name=form.cleaned_data['name'] + " " +
                                                      form.cleaned_data['last_name'],
                                            email=form.cleaned_data['email'])
            user.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse("index:home", args=()))

        return render(request, 'register.html', {"form": form})


class LogOutView(View):

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return HttpResponseRedirect(reverse("index:home", args=()))


class FavoriteBooks(View):

    def get(self, request, *args, **kwargs):
        books = DataQuery.get_favorite_books(request.user.id)
        return render(request, 'favorite_books.html',
                      {"books": json.dumps(books), "categories": Categories.objects.filter(level=0)})


class AddBook(View):

    def get(self, request, *args, **kwargs):
        form = AddBookForm(request.POST or None)
        file_form = FileUploadForm(request.POST or None)
        set_category_form = SetCategoryForm(request.POST or None)
        buffer = BufferFiles.objects.filter(user=request.user)
        return render(request, 'add_book.html',
                      {"form": form, "file_form": file_form, "set_category_form": set_category_form, "files": "s",
                       'buffer': buffer})

    def post(self, request, *args, **kwargs):
        form = AddBookForm(request.POST, request.FILES)
        file_form = FileUploadForm(request.POST, request.FILES)
        set_category_form = SetCategoryForm(request.POST)
        if form.is_valid() and set_category_form.is_valid():
            return add_book(form, set_category_form, file_form, request.user)
        return render(request, 'add_book.html',
                      {"form": form, 'file_form': file_form, "set_category_form": set_category_form,
                       "files": "s"})


class LoadBufferBookView(View):

    def post(self, request, *args, **kwargs):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            if kwargs['state'] == 0:
                buffer_file = BufferFiles.objects.create(file=form.cleaned_data['file'], user=request.user)
            else:
                buffer_file = BookFiles.objects.create(book_id=kwargs['book_id'], file=form.cleaned_data['file'],
                                                       expansion=form.cleaned_data['file'].name.split('.')[-1])

            return JsonResponse({'url': str(buffer_file.file.name)})
        return JsonResponse({'error': "Сталася помилка"})


class DeleteBufferView(View):

    def get(self, request, *args, **kwargs):
        if kwargs['state'] == 0:
            buffer = BufferFiles.objects.get(file__contains=kwargs['name'], user=request.user)
            buffer.delete()
        else:
            buffer_file = BookFiles.objects.get(book__upload_author=request.user, file__contains=kwargs['name'])

            buffer_file.delete()
        return JsonResponse({})


class BookView(View):

    def get(self, request, *args, **kwargs):
        form = CommentForm(request.POST or None)
        book = get_object_or_404(Book, id=kwargs['book_id'])
        book.views += 1
        book.save()
        whether_book_is_favorite = DataQuery.whether_book_is_favorite(request.user.id, book.id)
        if whether_user_can_open_book(request.user, book):
            return render(request, "book.html", {"book": book, 'form': form, 'favorite_book': whether_book_is_favorite})
        else:
            raise Http404("В вас не має прав на данну книгу")


class AddCommentView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST or None)
        book = get_object_or_404(Book, id=kwargs['book_id'])
        if form.is_valid():
            Comment.objects.create(book=book, user=request.user, comment_text=form.cleaned_data['comment_text'])
            data = {"username": request.user.username, 'comment_text': form.cleaned_data['comment_text']}
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'error'})


class EditBook(View):

    @only_for_book_owners
    def get(self, request, *args, **kwargs):
        book = kwargs['book']
        form = AddBookForm(request.POST or None,
                           initial={'title': book.title, 'author': book.author, 'description': book.description,
                                    'category': book.category.id, 'is_public': book.is_public,
                                    'series': book.series,
                                    'edition': book.edition, 'count_of_pages': book.count_of_pages,
                                    'translator': book.translator})
        file_form = FileUploadForm(request.POST or None)
        set_category_form = SetCategoryForm(request.POST or None, initial={'category': book.category})
        return render(request, 'edit_book.html',
                      {"form": form, 'file_form': file_form, "categories": Categories.objects.filter(level=0),
                       'book': book, "set_category_form": set_category_form, "files": "s",
                       'buffer': BookFiles.objects.filter(book=book)})

    @only_for_book_owners
    def post(self, request, *args, **kwargs):
        book = kwargs['book']
        form = AddBookForm(request.POST, request.FILES,
                           initial={'title': book.title, 'author': book.author, 'description': book.description,
                                    'category': book.category.id, 'isPublic': book.is_public,
                                    'series': book.series,
                                    'edition': book.edition, 'countOfPages': book.count_of_pages,
                                    'translator': book.translator})
        file_form = FileUploadForm(request.POST, request.FILES)
        set_category_form = SetCategoryForm(request.POST, initial={'category': book.category})
        if not BookFiles.objects.filter(book=book):
            errors = file_form.errors.setdefault("file", ErrorList())
            errors.append("Ви маєте внести хоча б один файл")
        if form.is_valid() and set_category_form.is_valid():
            DataQuery.edit_book(edited_book_data=form.cleaned_data.copy(),
                                category_data=set_category_form.cleaned_data.copy(), book_id=book.id)
            return HttpResponseRedirect(reverse('index:my_books', args=()))
        return render(request, 'edit_book.html',
                      {"form": form, 'file_form': file_form, "categories": Categories.objects.filter(level=0),
                       'book': book, "set_category_form": set_category_form, "files": "s",
                       'buffer': BookFiles.objects.filter(book=book)})


class AdminEditBookView(View, PermissionRequiredMixin):
    permission_required = 'admin'

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=kwargs['book_id'])
        form = ReasonForm(request.POST or None)
        return render(request, 'admin_edit_book.html',
                      {"form": form, 'book': book, "categories": Categories.objects.filter(level=0),
                       "ban_param": book.can_change_public})

    def post(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=kwargs['book_id'])
        form = ReasonForm(request.POST)
        if form.is_valid():
            DataQuery.change_books_visibility({'bookId': book.id, 'userId': request.user.id,
                                               'reason': form.cleaned_data['reason'],
                                               'canBookChangePublic': book.can_change_public})
            return HttpResponseRedirect(reverse("index:home", args=()))

        return render(request, 'admin_edit_book.html',
                      {"form": form, 'book': book, "ban_param": book.can_change_public,
                       "categories": Categories.objects.filter(level=0)})


class DeleteBookView(View):

    def get(self, request, *args, **kwargs):
        successful = DataQuery.delete_book(kwargs['book_id'], request.user.id)
        if successful:
            return HttpResponseRedirect(reverse("index:my_books", args=()))
        else:
            raise Http404("Ви не маєте прав на цю книгу")


class SearchView(View):

    def get(self, request, *args, **kwargs):
        title = kwargs['title']
        author = kwargs['author']
        title_ = title
        author_ = author
        if title == 'n':
            title_ = ''
        if author == 'n':
            author_ = ''

        category_id = kwargs['category_id']
        if category_id:
            category = Categories.objects.get(id=category_id)
        else:
            category = None
        form = SearchBookForm(request.POST or None, initial={"title": title_, 'author': author_,
                                                             "category": category})
        books = DataQuery.search_books(title_, author_, category_id)
        return render(request, "search.html",
                      {"books": json.dumps(books), "form": form, "title": title, "author": author, "category_id": category_id
                       })

    def post(self, request, *args, **kwargs):
        form = SearchBookForm(request.POST or None)
        if form.is_valid():

            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            category = form.cleaned_data['category']
            category_id = 0
            if category:
                category_id = category.id
            books = DataQuery.search_books(title, author, category_id)

        if author == '':
            author = 'n'

        if title == '':
            title = 'n'

        return render(request, "search.html",
                      {"books": json.dumps(books), "form": form, "title": title, "author": author, "category_id": category_id})


class AccountSettingsView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'account_settings.html', {"categories": Categories.objects.filter(level=0)})


class ChangePasswordView(View):

    def get(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST or None)

        return render(request, "change_password.html", {"categories": Categories.objects.filter(level=0), "form": form})

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            password = form.cleaned_data['password1']
            request.user.set_password(password)
            request.user.save()
            auth.login(request, user)
            return HttpResponseRedirect(reverse("index:account_settings"))
        return render(request, "change_password.html", {"categories": Categories.objects.filter(level=0), "form": form})


class ChangeUserDataView(View):

    def get(self, request, *args, **kwargs):
        user = request.user
        first_name = user.last_name.split(" ")[0]
        name = user.first_name
        last_name = user.last_name.split(" ")[1]
        form = ChangeUserDataForm(request.POST or None,
                                  initial={"email": user.email, "username": user.username, "first_name": first_name,
                                           "name": name, "last_name": last_name})
        return render(request, "change_user_data.html",
                      {"categories": Categories.objects.filter(level=0), "form": form})

    def post(self, request, *args, **kwargs):
        user = request.user
        first_name = user.last_name.split(" ")[0]
        name = user.first_name
        last_name = user.last_name.split(" ")[1]
        form = ChangeUserDataForm(request.POST or None,
                                  initial={"email": user.email, "username": user.username, "first_name": first_name,
                                           "name": name, "last_name": last_name})
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            request.user.first_name = name
            request.user.last_name = " ".join([first_name, last_name])
            request.user.email = email
            request.user.username = username
            request.user.save()
            return HttpResponseRedirect(reverse("index:account_settings"))
        return render(request, "change_user_data.html",
                      {"categories": Categories.objects.filter(level=0), "form": form})


class AdminMessangesView(PermissionRequiredMixin, View):
    permission_required = 'auth.admin'

    def get(self, request, *args, **kwargs):
        messanges = Info.objects.filter(type='a', answer_state='p')
        return render(request, "admin_messanges.html",
                      {"categories": Categories.objects.filter(level=0), 'messanges': messanges})


class Messanges(View):
    """Displays all messages about blocking user's books"""

    def get(self, request, *args, **kwargs):
        messanges = request.user.info_set.all()
        return render(request, "messanges.html",
                      {"categories": Categories.objects.filter(level=0), 'messanges': messanges})


class SendAnswerView(View):
    """Ajax view for sending info about changing book data for unblocking book"""

    def get(self, request, *args, **kwargs):
        DataQuery.send_answer(kwargs['messange_id'])
        return HttpResponseRedirect(reverse('index:messanges', args=()))


class AcceptAnswerView(PermissionRequiredMixin, View):
    """Ajax view for unblocking book and sending message about this to user"""
    permission_required = 'auth.admin'

    def get(self, request, *args, **kwargs):
        DataQuery.accept_answer(kwargs['messange_id'])
        return JsonResponse({})


class NotAcceptAnswerView(PermissionRequiredMixin, View):
    """Ajax view for recall request user's unblocking book message"""
    permission_required = 'auth.admin'

    def get(self, request, *args, **kwargs):
        DataQuery.not_accept_answer(kwargs['messange_id'])
        return JsonResponse({})


class DeleteMessangeView(PermissionRequiredMixin, View):
    permission_required = 'auth.admin'

    def get(self, request, *args, **kwargs):
        messange = get_object_or_404(Info, id=kwargs['messange_id'])
        messange.delete()
        return JsonResponse({})


class ChangeFavoriteView(View):

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=kwargs['book_id'])
        try:
            favorite_book = FavoriteBooksModel.objects.get(user=request.user, book=book)
        except FavoriteBooksModel.DoesNotExist:
            favorite_book = None

        if favorite_book:
            favorite_book.delete()
            return JsonResponse({"btn_text": "Додати в улуюлені"})
        else:
            FavoriteBooksModel.objects.create(user=request.user, book=book)
            return JsonResponse({"btn_text": "Забрати з улюблених"})


class CreateCategoryView(View):
    pass
