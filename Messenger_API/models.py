from django.db import models

class UserModel(models.Model):
    phone_number = models.CharField(max_length=11, unique=True, null=False, blank=False)
    profile_id = models.CharField(max_length=10, unique=True, null=True, default=None)
    first_name = models.CharField(max_length=15, null=True)
    last_name = models.CharField(max_length=15, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    def __str__(self):
        return self.profile_id
    
class MessageModel(models.Model):
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"From: {self.sender.profile_id} | To: {self.receiver.profile_id}"