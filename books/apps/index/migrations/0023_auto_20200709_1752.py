# Generated by Django 3.0.6 on 2020-07-09 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0022_categoryrating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookrating',
            name='view',
            field=models.IntegerField(default=False),
        ),
    ]