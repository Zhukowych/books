# Generated by Django 3.0.6 on 2020-06-01 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_auto_20200601_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
