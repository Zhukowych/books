from django.http import Http404
from django.shortcuts import get_object_or_404
import graphene
from django.db.models import Q
from .mutations import Mutation, Upload
from .types import *


class Query(graphene.ObjectType):
    books = graphene.List(BookType, user_id=graphene.Int())
    my_books = graphene.List(BookType, user_id=graphene.Int())
    books_from_category = graphene.List(BookType, user_id=graphene.Int(), category_id=graphene.Int())
    favorite_books = graphene.List(FavoriteBookType, user_id=graphene.Int())
    children_categories = graphene.List(CategoriesType, category_id=graphene.Int())
    search_books = graphene.List(BookType, title=graphene.String(), author=graphene.String(),
                                 category_id=graphene.Int())
    whether_book_is_favorite = graphene.Boolean(user_id=graphene.Int(), book_id=graphene.Int())

    @staticmethod
    def resolve_books(self, info, user_id):
        return Book.objects.filter(is_public=True).order_by("-rating")

    @staticmethod
    def resolve_my_books(self, info, user_id):
        return Book.objects.filter(upload_author__id=user_id)

    @staticmethod
    def resolve_books_from_category(self, info, user_id, category_id):
        user = User.objects.get(id=user_id)
        category = get_object_or_404(Categories, id=category_id)
        branch = category.get_descendants(include_self=True)
        return Book.objects.filter(is_public=True, category__in=branch).order_by('-rating')

    @staticmethod
    def resolve_favorite_books(self, info, user_id):
        return FavoriteBooksModel.objects.filter(user__id=user_id)

    @staticmethod
    def resolve_children_categories(self, info, category_id):
        category = get_object_or_404(Categories, id=category_id)
        return category.get_children()

    @staticmethod
    def resolve_search_books(self, info, title, author, category_id):
        if category_id:
            category = Categories.objects.get(id=category_id)
            categories_ids = category.get_descendants(include_self=True).values_list('id')
            books = Book.objects.filter(title__contains=title, author__contains=author,
                                        category_id__in=categories_ids, is_public=True)
        else:
            books = Book.objects.filter(title__contains=title, author__contains=author, is_public=True)
        return books

    @staticmethod
    def resolve_whether_book_is_favorite(self, info, user_id, book_id):
        try:
            FavoriteBooksModel.objects.get(user_id=user_id, book_id=book_id)
            whether_book_is_favorite = True
        except FavoriteBooksModel.DoesNotExist:
            whether_book_is_favorite = False
        return whether_book_is_favorite


schema = graphene.Schema(query=Query, mutation=Mutation, types=[Upload])
