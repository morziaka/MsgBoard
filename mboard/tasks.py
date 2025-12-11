from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail

from mboard.models import Reply, Post


@shared_task
def send_response_accept(reply_id):
    reply = Reply.objects.get(id=reply_id)  # получаем объект Reply
    reply_author_email = reply.author.email  # получаем email автора отклика Reply
    post = reply.reply  # получаем объект Post (объявление), связанный с Reply
    author = post.author  # Получаем объект User (автор объявления)
    # подготавливаем и отправляем письмо
    send_mail(
        subject='Ваш отклик был принят!',
        message=(
            f'Привет, {reply.author}! Ваш отклик на пост "{post.title}" был принят автором {author}. '
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reply_author_email],
        fail_silently=True
    )



@shared_task
def send_response_reject(reply_id):
    reply = Reply.objects.get(id=reply_id)  # получаем объект Reply
    reply_author_email = reply.author.email  # получаем email автора отклика Reply
    post = reply.reply  # получаем объект Post (объявление), связанный с Reply
    author = post.author  # Получаем объект User (автор объявления)
    # подготавливаем и отправляем письмо
    send_mail(
        subject='Ваш отклик был отклонен',
        message=(
            f'Привет, {reply.author}! К сожалению, Ваш отклик на пост "{post.title}" был отклонен автором {author}. '

        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reply_author_email],
        fail_silently=True
    )

@shared_task
def subscribers_notification_task(**params):
    send_mail(**params)

@shared_task
def subscribers_notification_weekly():
    before_datetime = timezone.now() - timedelta(days=7)
    posts = Post.objects.filter(time_post__gte=before_datetime)
    subscribers = User.objects.all()
    for subscriber in subscribers:
        text = ''
        for post in posts:
            category = post.categories
            if subscriber.email and category in subscriber.categories.all():
                queryset = posts.filter(categories=category).values("title", "id")
                for query in queryset:
                    text = text + f'<a href = "{settings.SITE_URL}/posts/{int(query["id"])}">{str(query["title"])}</a> \n'
        if text != '':
            send_mail(
                subject=f'Новинки за неделю на Новостном портале',
                message=(
                    f'Привет, {subscriber.username}! Ознакомьтесь с новинками за неделю по вашим подпискам. \n'
                    f'Список статей: \n {text}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                fail_silently=True
            )