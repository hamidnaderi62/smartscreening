from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from .models import Organization, Profile

User = get_user_model()

def org_register_fa(request, org_slug):
    # Get the organization or return 404
    organization = get_object_or_404(Organization, slug=org_slug)

    if request.user.is_authenticated:
        return redirect('home:home_fa')  # Adjust to your home URL

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "کلمه های عبور یکسان نمی باشند")
            return render(request, 'account/org_register_fa.html', {'organization': organization})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "نام کاربری تکراری می باشد")
            return render(request, 'account/org_register_fa.html', {'organization': organization})

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        # Create profile and associate with organization
        Profile.objects.create(
            user=user,
            organization=organization,
            code=organization.code  # Or generate a unique code
        )

        login(request, user)
        request.session['organization_id'] = organization.id
        request.session['user_type'] = user.profile.user_type
        request.session['username'] = user.username

        return redirect('home:home_fa')  # Adjust to your home URL

    return render(request, 'account/org_register_fa.html', {'organization': organization})

def org_login_fa(request, org_slug):
    # Redirect if already logged in
    organization = get_object_or_404(Organization, slug=org_slug)

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
            return render(request, 'account/org_login_fa.html', {'organization': organization})

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Reset attempt counter
            cache.delete(cache_key)

            print(organization)
            print(user.profile.organization)
            if user.profile.organization == organization:
                login(request, user)
                request.session['organization_id'] = organization.id
                request.session['organization_slug'] = organization.slug
                request.session['user_type'] = user.profile.user_type
                request.session['username'] = user.username

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
                messages.error(request, "شما عضو این سازمان نیستید")

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

    return render(request, 'account/org_login_fa.html', {'organization': organization})

def org_logout_fa1(request):
    # Store organization slug before clearing session
    org_slug = None
    if 'organization_id' in request.session:
        try:
            organization = Organization.objects.get(id=request.session['organization_id'])
            org_slug = organization.slug
        except (KeyError, Organization.DoesNotExist):
            pass

    # Logout and clear session
    logout(request)
    request.session.flush()  # This clears all session data

    # Redirect appropriately
    if org_slug:
        return redirect('account:org_login_fa', org_slug=org_slug)
    else:
        return redirect('home:home_fa')  # Fallback redirect

def org_logout_fa(request):
    # Store organization slug before clearing session
    org_slug = None
    if 'organization_slug' in request.session:
        try:
            org_slug = request.session['organization_slug']
        except (KeyError, Organization.DoesNotExist):
            pass

    # Logout and clear session
    logout(request)
    request.session.flush()  # This clears all session data
    request.session['organization_slug'] = org_slug

    # Redirect appropriately
    if org_slug:
        return redirect('account:org_login_fa', org_slug=org_slug)
    else:
        return redirect('home:home_fa')  # Fallback redirect

