# Generated by Django 3.0.6 on 2020-06-01 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_book_bookimagelink_booklink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='book',
            name='rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='book',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]