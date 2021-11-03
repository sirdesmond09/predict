from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=360)
    body = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    likers = models.ManyToManyField(User, blank=True, related_name='likers')
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    
    def delete(self):
        self.is_active=False
        self.save()
        
    def __str__(self):
        return self.title
    
    

