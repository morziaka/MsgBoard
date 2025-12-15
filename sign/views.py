
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.shortcuts import render, redirect
from .models import OneTimeCode
from .utils import generate_otp, verify_otp
from django.core.mail import send_mail
from django.conf import settings



def register(request):
    if request.method == 'POST':

        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']

            if not all([username, email, password]):
                return render(request, 'sign/signup.html', {'error': 'Заполнены не все поля.'})

            # Важно: Используйте create_user для хеширования пароля
            user = User.objects.create_user(username=username, email=email, password=password)
            # Generate and save OTPs
            email_otp = generate_otp()
            code = OneTimeCode.objects.create(receiver=user, email_otp=email_otp)
            user.save()
            code.save()

            # Send email OTP
            send_mail(
                'Ваш код регистрации',
                f'Ваш код регистрации: {email_otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return redirect('verify_code', user_id=user.id)

        except IntegrityError:
            if User.objects.filter(username=username).exists():
                context = f'Пользователь {username}  уже существует.'
            elif User.objects.filter(email=email).exists():
                context = f'Пользователь с адресом {email} уже существует.'
            return render(request, 'sign/signup.html', {'error': context})


    return render(request, 'sign/signup.html')

def verify_code(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        email_otp = request.POST['email_otp']
        code = OneTimeCode.objects.get(receiver_id=user.id)
        confirmed_users = Group.objects.get(name='Confirmed')

        if code.is_expired():
            print('expired')
            code.delete()
            email_otp = generate_otp()
            code = OneTimeCode.objects.create(receiver = user, email_otp = email_otp)
            email = user.email
            send_mail(
                'Ваш код регистрации',
                f'Ваш код регистрации: {email_otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return render(request, 'sign/verify_otp.html', {'error': 'Срок действия кода истек. Введите новый код.'})
        else:

            if verify_otp(email_otp, code.email_otp):
                code.is_email_verified = True
                code.email_otp = None
                if not user.groups.filter(name='Confirmed').exists():
                    user.groups.add(confirmed_users)
                user.save()
                login(request, user)
                return render(request, 'sign/login.html')
            else:
                return render(request, 'sign/verify_otp.html', {'error': 'Неверный код'})

    return render(request, 'sign/verify_otp.html')

def confirm_logout(request):
    return render(request, 'sign/confirm_logout.html')

@login_required
def user_profile(request):
    context = {
        'is_confirmed': request.user.groups.filter(name='Confirmed').exists(),
    }
    return render(request, 'sign/profile.html', context)



