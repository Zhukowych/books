# Generated by Django 3.1.4 on 2020-12-15 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0024_auto_20200709_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='is_public',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
