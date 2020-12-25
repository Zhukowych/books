from django import forms
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
    category_id = Categories.objects.get(name=form.cleaned_data['category']).id
    if form.cleaned_data['is_public'] == 'так':
        is_public = 1
    elif form.cleaned_data['is_public'] == 'ні':
        is_public = 0
    else:
        is_public = 2
    return HttpResponseRedirect(reverse('index:search', args=(title, author,
                                                              category_id, is_public,
                                                              )))


def add_book(add_book_form: AddBookForm, set_category_form: SetCategoryForm,
             file_form: FileUploadForm, user: SimpleLazyObject) -> HttpResponseRedirect:
    image = add_book_form.cleaned_data['image']
    DataQuery.upload_book_image_link(image)
    image_link = BookImageLink(image_link=image)
    image_link.save()
    is_public = add_book_form.cleaned_data['isPublic']

    category = set_category_form.cleaned_data['category']
    name = set_category_form.cleaned_data['name']
    parent_category = set_category_form.cleaned_data['parent_category']

    if category:
        category = category
    else:
        category = Categories.objects.create(name=name, parent=parent_category)

    book_id = DataQuery.create_book(add_book_form.cleaned_data, user.id, category.id, image_link.id)
    DataQuery.move_book_files_from_buffer_to_vault(user.id, book_id)
    return HttpResponseRedirect(reverse("index:book", args=(book_id,)))


def clean_add_form(data):
    for format in data.values():
        if format:
            return
    raise forms.ValidationError('ви маєте вказати хоча б один формат книги')
