from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.query import QuerySet
from django.utils.functional import SimpleLazyObject
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from .forms import SearchBookForm, AddBookForm, SetCategoryForm, FileUploadForm
from .models import Categories, Book, BookImageLink, BufferFiles, BookFiles
from .DataQuery import DataQuery


def search_in_my_books(form: SearchBookForm, user: SimpleLazyObject) -> QuerySet:
    title = form.cleaned_data['title']
    author = form.cleaned_data['author']
    category_name = form.cleaned_data['category']
    is_public = form.cleaned_data['is_public']
    category_id = Categories.objects.get(name=category_name).id

    if is_public == 'ні':
        books = Book.objects.filter(title__contains=title, author__contains=author, category_id=category_id,
                                    is_public=False).order_by('-rating')
    elif is_public == "так":
        books = user.book_set.filter(title__contains=title, author__contains=author,
                                     category_id=category_id, is_public=True).order_by('-rating')
    else:
        books = user.book_set.filter(title__contains=title, author__contains=author,
                                     category_id=category_id).order_by('-rating')
    return books


def get_data_from_search_form(form: SearchBookForm) -> HttpResponseRedirect:
    title = form.cleaned_data['title']
    author = form.cleaned_data['author']
    if title == '':
        title = "n"
    if author == '':
        author = "n"
    if form.cleaned_data['category']:
        category_id = form.cleaned_data['category'].id
    else:
        category_id = 0

    return HttpResponseRedirect(reverse('index:search', args=(title, author,
                                                              category_id
                                                              )))


def add_book(add_book_form: AddBookForm, set_category_form: SetCategoryForm,
             file_form: FileUploadForm, user: SimpleLazyObject) -> HttpResponseRedirect:
    image_link_id = DataQuery.upload_book_image_link(add_book_form.cleaned_data['image'])
    category_id = DataQuery.get_or_create_category_for_book(set_category_form.cleaned_data)
    book_id = DataQuery.create_book(add_book_form.cleaned_data, user.id, category_id, image_link_id)
    DataQuery.move_book_files_from_buffer_to_vault(user.id, book_id)
    return HttpResponseRedirect(reverse("index:book", args=(book_id,)))


def clean_add_form(data):
    for format in data.values():
        if format:
            return
    raise forms.ValidationError('ви маєте вказати хоча б один формат книги')


"""--HELPERS-BEAUTIFULERS--"""


def whether_user_can_open_book(user: SimpleLazyObject, book: Book):
    if user.is_authenticated and book.is_public:
        return True
    elif not user.is_authenticated and book.is_public:
        return True
    elif not book.is_public and book.upload_author == user:
        return True
    else:
        return False


def is_favorite_book():
    pass
