from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from .models import OneTimeCode
from .utils import generate_otp, verify_otp
from django.core.mail import send_mail
from django.conf import settings



def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=email
                                              , password=password)

        # Generate and save OTPs
        email_otp = generate_otp()
        code = OneTimeCode.objects.create(receiver = user, email_otp = email_otp)

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

    return render(request, 'sign/signup.html')

def verify_code(request, user_id):
    user = User.objects.get(id=user_id)
    print(user.id)


    if request.method == 'POST':
        email_otp = request.POST['email_otp']
        code = OneTimeCode.objects.get(receiver_id=user.id)
        confirmed_users = Group.objects.get(name='Confirmed')

        if verify_otp(email_otp, code.email_otp):
            user.is_email_verified = True
            user.email_otp = None
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



