# Generated by Django 5.0.6 on 2024-07-12 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger_API', '0006_alter_usermodel_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagemodel',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='attachments/'),
        ),
    ]
