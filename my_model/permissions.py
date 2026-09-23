from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from account.models import OrganizationMembership

from .models import MyModel


User = get_user_model()


def can_view_screening(user, target_user):
    """Return whether ``user`` may view screening data belonging to ``target_user``."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    target_has_membership = OrganizationMembership.objects.filter(
        user=target_user,
        is_active=True,
    ).exists()
    if user.pk == target_user.pk:
        # Personal users without an organization remain allowed to see their
        # own reports; deactivated organization members do not.
        return target_has_membership or not OrganizationMembership.objects.filter(
            user=target_user,
        ).exists()

    admin_organization_ids = OrganizationMembership.objects.filter(
        user=user,
        role='admin',
        is_active=True,
    ).values_list('organization_id', flat=True)
    target_organization_ids = OrganizationMembership.objects.filter(
        user=target_user,
        is_active=True,
    ).values_list('organization_id', flat=True)

    return target_has_membership and target_organization_ids.filter(
        organization_id__in=admin_organization_ids,
    ).exists()


def screening_queryset_for_user(user, *, code=None, target_user_id=None):
    """Build the only queryset that report endpoints should use."""
    if not user or not user.is_authenticated:
        return MyModel.objects.none()

    user_memberships = OrganizationMembership.objects.filter(user=user)
    if user_memberships.exists() and not user_memberships.filter(is_active=True).exists():
        return MyModel.objects.none()

    if target_user_id is not None:
        target_user = get_object_or_404(User, pk=target_user_id)
        if not can_view_screening(user, target_user):
            return MyModel.objects.none()
        queryset = MyModel.objects.filter(userid=target_user)
    elif user.is_superuser:
        queryset = MyModel.objects.all()
    else:
        admin_organization_ids = OrganizationMembership.objects.filter(
            user=user,
            role='admin',
            is_active=True,
        ).values_list('organization_id', flat=True)
        if admin_organization_ids:
            queryset = MyModel.objects.filter(
                userid__organization_memberships__organization_id__in=admin_organization_ids,
                userid__organization_memberships__is_active=True,
            )
        else:
            queryset = MyModel.objects.filter(userid=user)

    if code and target_user_id is None:
        queryset = queryset.filter(code=code)
    return queryset
