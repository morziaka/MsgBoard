"""


The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
# Импортируем созданное нами представление
from .views import *
from django.views.decorators.cache import cache_page


urlpatterns = [
   path('', PostsList.as_view(), name = "post_list"),
   path('posts/', PostsList.as_view(), name = "post_list"),
   path('<int:pk>', PostDetail.as_view(), name = "post_detail"),
   path('post/create/', PostCreate.as_view(), name= "post_create"),
   path('post/<int:pk>/reply/create/', ReplyCreate.as_view(), name= "reply_create"),
   path('replies/', RepliesList.as_view(), name= "replies"),
   path('post/<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
   path('post/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('categories/', CategoryListView.as_view(), name = 'category_list'),
   path('category/<int:pk>/subscribe/', subscribe, name = 'subscribe'),
   path('category/<int:pk>/unsubscribe/', unsubscribe, name = 'unsubscribe'),
    path('post/<int:post_id>/replies/accept/<int:reply_id>', response_accept,
         name='response_accept'),
    path('post/<int:post_id>/replies/reject/<int:reply_id>', response_reject,
         name='response_reject'),
]