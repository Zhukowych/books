# Generated by Django 3.0.6 on 2020-06-15 09:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('index', '0017_auto_20200615_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookfiles',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='books/', verbose_name=''),
        ),
        migrations.CreateModel(
            name='BufferFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
