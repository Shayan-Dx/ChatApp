# Generated by Django 5.0.6 on 2024-07-31 15:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Messenger_API', '0007_messagemodel_attachment'),
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagemodel',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='Users.usermodel'),
        ),
        migrations.AlterField(
            model_name='messagemodel',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='Users.usermodel'),
        ),
        migrations.DeleteModel(
            name='UserModel',
        ),
    ]
