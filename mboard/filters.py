
from django.contrib.auth.models import User
from django_filters import FilterSet, ModelChoiceFilter
from .models import Post

def posts(request):
    if request is None:
        return User.objects.none()
    author = request.user.id
    post = Post.objects.filter(author = author)
    return post

class PostFilter(FilterSet):

    title = ModelChoiceFilter(queryset= posts, label="Объявления", empty_label="Все объявления")


    class Meta:
       model = Post
       fields = ['title']




