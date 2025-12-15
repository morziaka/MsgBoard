from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save
from .tasks import subscribers_notification_task

from .models import Category, Post


@receiver(post_save, sender = Post)
def newpost_notification(sender, instance, created, **kwargs):
    if created:
        current_category = instance.categories
        emails = []
        subscribers = current_category.subscribers.all()
        for user in subscribers:
            if user.email and user.email not in emails:
                html_content = (
                        f'<p>Привет, {user.username}! На Новостном портале новая публикация "{instance.title}" в категории: {instance.categories}. </p>'
                        f'<p>Краткое содержание: {instance.Preview()}</p>'
                        f'<p>Полный текст публикации <a href = "{settings.SITE_URL}/posts/{instance.id}">по этой ссылке</a></p>'
                    )
                params = {
                        'subject': 'Новая публикация на Новостном портале',
                        'message':
                        f'Привет, {user.username}! На Новостном портале новая публикация "{instance.title}" в категории: {instance.categories}. \n'
                        f'Краткое содержание: {instance.Preview()}.'
                        f'Полный текст публикации <a href = "{settings.SITE_URL}/posts/{instance.id}">по этой ссылке</a>',
                        'html_message' : html_content,
                        'from_email': settings.DEFAULT_FROM_EMAIL,
                        'recipient_list' : [user.email],
                        'fail_silently' : True
                    }
                emails.append(user.email)
                subscribers_notification_task.delay(**params)


@receiver(m2m_changed, sender = Category.subscribers.through)
def subscribers_notification(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        user = User.objects.get(pk__in=pk_set)
        send_mail(
            subject='Новая подписка',
            message=(
                f'Привет, {user.username}! Вы подписались на категорию {instance.name}. '
                f'Ваши текущие подписки: {", ".join(cat.name for cat in user.categories.all())}'
                ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

    if action == 'post_remove':
        user = User.objects.get(pk__in=pk_set)
        send_mail(
            subject='Отписка от категории',
            message=(
                f'Привет, {user.username}! Вы отписались от категории {instance.name}. '
                f'Ваши текущие подписки: {", ".join(cat.name for cat in user.categories.all())}'
                ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

