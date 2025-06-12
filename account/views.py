from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.conf import settings

User = get_user_model()

from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType


def user_login_fa(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('/home_fa')

    User = get_user_model()

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # 'on' or None

        # Rate limiting check
        cache_key = f'login_attempts_{username}'
        login_attempts = cache.get(cache_key, 0)

        if login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            messages.error(request, "تعداد تلاش‌های شما بیش از حد بوده است. لطفاً 30 دقیقه دیگر تلاش کنید.")

            # Log the lockout with system user or anonymous user fallback
            try:
                system_user = User.objects.get(username='system')
            except User.DoesNotExist:
                system_user = User.objects.first()  # Fallback to first admin user

            LogEntry.objects.log_action(
                user_id=system_user.id,  # Never pass None
                content_type_id=ContentType.objects.get_for_model(User).pk,
                object_id=None,
                object_repr=f'Account locked: {username}',
                action_flag=ADDITION,
                change_message=f'IP: {request.META.get("REMOTE_ADDR")}'
            )
            return render(request, 'account/login_fa.html')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Reset attempt counter
            cache.delete(cache_key)
            login(request, user)

            # Set session expiry
            request.session.set_expiry(None if remember_me == 'on' else 0)

            # Log successful login
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(User).pk,
                object_id=user.id,
                object_repr=f'Successful login: {username}',
                action_flag=ADDITION,
                change_message=f'IP: {request.META.get("REMOTE_ADDR")}'
            )
            return redirect('/home_fa')
        else:
            # Increment failed attempt counter
            login_attempts += 1
            cache.set(cache_key, login_attempts, settings.LOGIN_ATTEMPTS_TIMEOUT)

            # Get system user for logging
            try:
                system_user = User.objects.get(username='system')
            except User.DoesNotExist:
                system_user = User.objects.first()  # Fallback to first admin user

            remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - login_attempts

            # Log failed attempt
            LogEntry.objects.log_action(
                user_id=system_user.id,  # Never pass None
                content_type_id=ContentType.objects.get_for_model(User).pk,
                object_id=None,
                object_repr=f'Failed login: {username}',
                action_flag=ADDITION,
                change_message=f'Remaining: {remaining_attempts}, IP: {request.META.get("REMOTE_ADDR")}'
            )

            if not User.objects.filter(username=username).exists():
                messages.error(request, "کاربری با این نام کاربری وجود ندارد")
            else:
                messages.error(request, f"نام کاربری یا رمز عبور اشتباه است. {remaining_attempts} تلاش باقی مانده")

    return render(request, 'account/login_fa.html')

def user_login_fa2(request):
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('/home_fa')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # 'on' or None

        # Rate limiting check
        cache_key = f'login_attempts_{username}'
        login_attempts = cache.get(cache_key, 0)

        if login_attempts >= settings.MAX_LOGIN_ATTEMPTS:  # Typically 5
            messages.error(request, "تعداد تلاش‌های شما بیش از حد بوده است. لطفاً 30 دقیقه دیگر تلاش کنید.")
            return render(request, 'account/login_fa.html')

        # Authenticate user (without manual password hashing)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Reset attempt counter on successful login
            cache.delete(cache_key)

            login(request, user)

            # Session expiration handling
            if remember_me == 'on':
                # Persistent session (default: 2 weeks)
                request.session.set_expiry(None)
            else:
                # Session expires when browser closes
                request.session.set_expiry(0)

            return redirect('/home_fa')
        else:
            # Increment failed attempt counter
            cache.set(cache_key, login_attempts + 1,
                      settings.LOGIN_ATTEMPTS_TIMEOUT)  # Typically 1800 seconds (30 mins)

            User = get_user_model()
            remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - login_attempts - 1

            if not User.objects.filter(username=username).exists():
                messages.error(request, "کاربری با این نام کاربری وجود ندارد")
            else:
                messages.error(request,
                               f"نام کاربری یا رمز عبور اشتباه است. شما {remaining_attempts} تلاش باقی مانده دارید.")

    return render(request, 'account/login_fa.html')

def user_login_fa1(request):
    if request.user.is_authenticated:
        return redirect('/home_fa')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            return redirect('/home_fa')
        else:
            from django.contrib.auth import get_user_model
            # User = get_user_model()

            if not User.objects.filter(username=username).exists():
                messages.error(request, "کاربری با این نام کاربری وجود ندارد")
            else:
                messages.error(request, "نام کاربری یا رمز عبور اشتباه است")

    return render(request, 'account/login_fa.html')


def user_logout(request):
    logout(request)
    return redirect('/')


def user_logout_fa(request):
    logout(request)
    return redirect('/home_fa')





def user_register_fa(request):
    if request.user.is_authenticated:
        return redirect('/home_fa')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "کلمه های عبور یکسان نمی باشند")
            return render(request, 'account/register_fa.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "نام کاربری تکراری می باشد")
            return render(request, 'account/register_fa.html')

        # Create user with hashed password (Method 1: Using create_user)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1  # Automatically hashed
        )

        login(request, user)
        return redirect('/home_fa')

    return render(request, 'account/register_fa.html')

