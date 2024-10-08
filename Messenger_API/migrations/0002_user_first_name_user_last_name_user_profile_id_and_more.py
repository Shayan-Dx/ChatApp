# Generated by Django 5.0.6 on 2024-07-06 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger_API', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_id',
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
