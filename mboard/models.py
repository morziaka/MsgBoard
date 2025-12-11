from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.urls import reverse
from froala_editor.fields import FroalaField
from froala_editor.widgets import FroalaEditor


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique = True)
    subscribers = models.ManyToManyField(User, related_name='categories')

    def __str__(self):
        return self.name

class Post(models.Model):

    time_post = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length = 100)
    content = FroalaField(options={
    'toolbarInline': False,
  })

    def __str__(self):
        return self.title

    def like(self):
        self.rating_post = self.rating_post + 1
        self.save()

    def dislike(self):
        self.rating_post = self.rating_post - 1
        self.save()

    def Preview(self):
        if len(self.content) <= 124:
            return self.content
        else:
            return self.content[0:123] + '...'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])



class Reply(models.Model):
    reply = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text_reply = models.TextField()
    time_reply = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=((0, 'Not considered'), (1, 'Accept'), (2, 'Reject')), default=0)



    def like(self):
        self.rating_comm = self.rating_comm + 1
        self.save()

    def dislike(self):
        self.rating_comm = self.rating_comm - 1
        self.save()



