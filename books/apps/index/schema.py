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

    @staticmethod
    def resolve_books(self, info, user_id):
        user = User.objects.get(id=user_id)
        return Book.objects.filter(Q(is_public=True) | Q(is_public=False, upload_author=user)).order_by("-rating")

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


schema = graphene.Schema(query=Query, mutation=Mutation, types=[Upload])
