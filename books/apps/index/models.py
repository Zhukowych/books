from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User


class BookImageLink(models.Model):
    image_link = models.ImageField(upload_to='book_images/', blank=True, null=True)


class Categories(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']


class Book(models.Model):
    upload_author = models.ForeignKey(User, related_name="users_book", on_delete=models.CASCADE, null=True)
    author = models.CharField(max_length=30, null=True)
    translator = models.CharField(max_length=30, null=True)
    series = models.CharField(max_length=30, null=True)
    count_of_pages = models.IntegerField(null=True)
    language = models.CharField(max_length=30, null=True)
    edition = models.CharField(max_length=30, null=True)
    title = models.TextField(null=True)
    can_change_public = models.BooleanField(default=True)
    image = models.ForeignKey(BookImageLink, on_delete=models.SET_NULL, null=True)
    category = TreeForeignKey(Categories, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True)
    date_uploaded = models.DateField()
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    is_public = models.BooleanField(default=False, null=True)


class BookFiles(models.Model):
    file = models.FileField('', upload_to="books/", blank=True, null=True)
    expansion = models.CharField(max_length=30)
    book = models.ForeignKey(Book, related_name="referenced_book_file", on_delete=models.CASCADE)


class BufferFiles(models.Model):
    file = models.FileField('', upload_to="buffer/", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Info(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=40, null=True)
    messange = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    type = models.CharField(max_length=5, null=True)
    answer_state = models.CharField(max_length=5, null=True)


class BookRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    view = models.IntegerField(default=False)


class CategoryRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    view = models.IntegerField(default=False)


class Reccomendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.FloatField()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment_text = models.TextField()


class FavoriteBooksModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
