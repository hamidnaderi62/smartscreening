from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_SIZE = 5 * 1024 * 1024


def validate_image_upload(value):
    """Validate size, MIME hint, and actual image contents for uploaded images."""
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError('Images must be smaller than 5 MB.')

    content_type = getattr(value, 'content_type', None)
    if content_type and not content_type.startswith('image/'):
        raise ValidationError('Only image files are allowed.')

    try:
        image = Image.open(value)
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError('The uploaded file is not a valid image.') from exc
    finally:
        value.seek(0)
