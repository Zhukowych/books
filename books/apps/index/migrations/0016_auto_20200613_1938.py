# Generated by Django 3.0.6 on 2020-06-13 16:38

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('index', '0015_favoritebooks'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FavoriteBooks',
            new_name='FavoriteBooksModel',
        ),
    ]
