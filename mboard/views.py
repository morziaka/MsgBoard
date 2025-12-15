from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from .models import Post, Category, Reply
from .filters import PostFilter
from .forms import PostForm, ReplyForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .tasks import send_response_accept, send_response_reject

from .utils import create_or_edit


class PostsList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    ordering = ['-time_post']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        path_create = reverse_lazy('post_create')
        return create_or_edit(context, self.request.path)

class RepliesList(FilterView):
    model = Post
    template_name = 'replies.html'
    context_object_name = 'posts'
    filterset_class = PostFilter
    ordering = ['-time_post']
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['replies'] = Reply.objects.filter(reply__author=self.request.user)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    form_class = ReplyForm
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['replies'] = Reply.objects.filter(reply__id=self.object.id)
        context['my_replies'] = Reply.objects.filter(reply__author=self.request.user, reply__id=self.object.id)
        return context



class PostCreate(PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create_or_update.html'
    permission_required = 'mboard.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        path = self.request.path
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        path_create = reverse_lazy('post_create')
        return create_or_edit(context, self.request.path)



class PostUpdate(PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create_or_update.html'
    permission_required = 'mboard.change_post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        path_create = reverse_lazy('post_update')
        return create_or_edit(context, self.request.path)

class PostDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    permission_required = 'mboard.delete_post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return create_or_edit(context, self.request.path)

class CategoryListView(PermissionRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    permission_required = 'mboard.add_post'

@login_required
def subscribe (request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def unsubscribe (request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER'))


class ReplyCreate(PermissionRequiredMixin, CreateView):
    form_class = ReplyForm
    model = Reply
    template_name = 'reply_create.html'
    success_url = reverse_lazy('post_list')
    permission_required = 'mboard.add_post'
    context_object_name = 'reply'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        post = Post.objects.get(id=kwargs['pk'])
        post_user_email = post.author.email  # Получаю email автора объявления, что бы использовать его при отправке email
        if form.is_valid():
            resp = form.save(commit=False)
            resp.author = request.user
            resp.reply = post
            resp.save()
            post_id = post.id  # Получаю идентификатор объявления, что бы использовать его в ссылке, в email
            send_mail(
                'Вам пришел новый отклик',
                f'Новый отклик на Ваш пост: <a href = "{settings.SITE_URL}/posts/{post_id}">смотреть</a>',
                settings.EMAIL_HOST_USER,
                [post_user_email],
                fail_silently=False,
            )

            return self.form_valid(form)



class ReplyDelete(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = 'reply_delete.html'
    pk_url_kwarg = 'reply_id'

    def get_success_url(self, post_id):
        post = Post.objects.get(pk=post_id)
        return redirect(pk=post_id)


@login_required
def response_accept(request, reply_id, post_id):
    post = Post.objects.get(pk=post_id)
    reply = Reply.objects.get(id=reply_id)
    reply.status = 1  # Изменяем статус на "Подтвержден"
    reply.save()
    send_response_accept(reply_id)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def response_reject(request, reply_id, post_id):
    post = Post.objects.get(pk=post_id)
    reply = Reply.objects.get(id=reply_id)
    reply.status = 2  # Изменяем статус на "Отклонен"
    reply.save()
    send_response_reject(reply_id)
    Reply.objects.filter(id=reply_id).delete()
    return redirect(request.META.get('HTTP_REFERER'))