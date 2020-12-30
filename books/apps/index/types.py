from django.contrib.auth.models import User
from graphene_django import DjangoObjectType

from .models import Book, BookImageLink, BookFiles, Categories, FavoriteBooksModel, BufferFiles, BookRating, CategoryRating, Info


class UserType(DjangoObjectType):
    class Meta:
        model = User


class BookType(DjangoObjectType):
    class Meta:
        model = Book


class BookFilesType(DjangoObjectType):
    class Meta:
        model = BookFiles


class BookImageLinkType(DjangoObjectType):
    class Meta:
        model = BookImageLink


class BufferFileType(DjangoObjectType):
    class Meta:
        model = BufferFiles


class CategoriesType(DjangoObjectType):
    class Meta:
        model = Categories


class FavoriteBookType(DjangoObjectType):
    class Meta:
        model = FavoriteBooksModel
