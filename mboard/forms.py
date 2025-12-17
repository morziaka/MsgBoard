from django import forms
from django.core.exceptions import ValidationError
from froala_editor.widgets import FroalaEditor

from .models import Post, Reply


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=FroalaEditor(options={
    'toolbarInline': False, 'videoInsertButtons': [    'videoBack',     '|',     'videoByURL', 'videoEmbed'  ]
  }))

    class Meta:
       model = Post

       fields = ['categories', 'title', 'content']

       labels = {
    'categories' : 'Категории',
    'title' : 'Название',
    'content' : 'Содержание',
       }
       widgets = {
           'content': FroalaEditor
       }


class ReplyForm(forms.ModelForm):
   class Meta:
       model = Reply
       fields = ['text_reply']
       labels = {
    'text_reply' : '',

       }