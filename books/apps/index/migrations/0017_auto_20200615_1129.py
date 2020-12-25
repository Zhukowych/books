# Generated by Django 3.0.6 on 2020-06-15 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0016_auto_20200613_1938'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='books/', verbose_name='книга pdf')),
                ('expansion', models.CharField(max_length=30)),
            ],
        ),
        migrations.RemoveField(
            model_name='book',
            name='book',
        ),
        migrations.DeleteModel(
            name='BookLink',
        ),
        migrations.AddField(
            model_name='bookfiles',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='index.Book'),
        ),
    ]
