from django.db import models

class User(models.Model):
    phone_number = models.CharField(max_length=11, unique=True, null=False)