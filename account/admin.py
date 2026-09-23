from django.contrib import admin
from . import models


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'code', 'default_language', 'admin_user', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'slug', 'code', 'admin_user__username')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Organization identity', {
            'fields': ('title', 'title_en', 'title_ar', 'code', 'slug', 'website', 'is_active'),
        }),
        ('Public page content', {
            'fields': ('sentence', 'sentence_en', 'sentence_ar', 'image', 'logo', 'default_language'),
        }),
        ('Authentication page branding', {
            'fields': ('brand_primary_color', 'brand_accent_color', 'brand_surface_color'),
            'description': 'These colors customize the organization login and registration pages.',
        }),
        ('Organization administration', {
            'fields': ('admin_user',),
        }),
    )

    def save_model(self, request, obj, form, change):
        previous_admin_id = None
        if change:
            previous_admin_id = models.Organization.objects.filter(pk=obj.pk).values_list('admin_user_id', flat=True).first()
        super().save_model(request, obj, form, change)
        if previous_admin_id and previous_admin_id != obj.admin_user_id:
            models.Profile.objects.filter(
                user_id=previous_admin_id,
                organization=obj,
                is_org_admin=True,
            ).update(user_type='Person', is_org_admin=False)
            models.OrganizationMembership.objects.filter(
                user_id=previous_admin_id,
                organization=obj,
            ).update(is_active=False)
        if obj.admin_user_id:
            profile, _ = models.Profile.objects.get_or_create(
                user=obj.admin_user,
                defaults={'code': str(obj.admin_user_id)},
            )
            profile.organization = obj
            profile.user_type = 'Organization'
            profile.is_org_admin = True
            if not profile.code:
                profile.code = str(obj.admin_user_id)
            profile.save(update_fields=('organization', 'user_type', 'is_org_admin', 'code'))
            models.OrganizationMembership.objects.update_or_create(
                user=obj.admin_user,
                organization=obj,
                defaults={'role': 'admin', 'is_active': True},
            )


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'phone_number', 'language', 'user_type', 'is_org_admin', 'code')
    list_filter = ('organization', 'user_type', 'is_org_admin')
    search_fields = ('user__username', 'user__email', 'code')


@admin.register(models.OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_active', 'created')
    list_filter = ('organization', 'role', 'is_active')
    search_fields = ('user__username', 'user__email', 'organization__title')

