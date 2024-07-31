from django.db import models

class UserModel(models.Model):
    phone_number = models.CharField(max_length=11, unique=True, null=False, blank=False)
    profile_id = models.CharField(max_length=10, unique=True, null=True, default=None)
    first_name = models.CharField(max_length=15, null=True)
    last_name = models.CharField(max_length=15, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    def __str__(self):
        return self.profile_id