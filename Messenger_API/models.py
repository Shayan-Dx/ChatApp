from django.db import models
from Users.models import UserModel
    
class MessageModel(models.Model):
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    
    def __str__(self):
        return f"From: {self.sender.profile_id} | To: {self.receiver.profile_id}"