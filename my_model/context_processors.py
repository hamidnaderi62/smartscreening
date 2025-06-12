def base_url(request):
    from django.conf import settings
    return {
        'SMARTLIFE_BASE_URL':settings.SMARTLIFE_BASE_URL,
        'SMARTLIFE_IMAGE_BASE_URL':settings.SMARTLIFE_IMAGE_BASE_URL
    }