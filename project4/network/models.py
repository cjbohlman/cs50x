from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    post_text = models.TextField(blank=True)
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="author")
    timestamp = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField()
    users_liked = models.ManyToManyField(User, blank=True, related_name="users_liked")

    def serialize(self):
        return {
            "id": self.id,
            "post_text": self.post_text,
            "author": self.author,
            "timestamp": self.timestamp.strftime("%b %-d %Y, %-I:%M %p"),
            "like_count": self.like_count,
            "users_liked": [user.username for user in self.users_liked.all()]
        }