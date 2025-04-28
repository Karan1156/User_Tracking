from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Visitor(models.Model):
    name=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    longitude=models.FloatField()
    latitude=models.FloatField()
    date=models.DateTimeField(auto_now_add=True)

class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    @property
    def image_or_default(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return "https://picsum.photos/800/400"



