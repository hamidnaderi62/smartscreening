"""Persistence services for screening records."""

import logging

from ..models import MyModel
from .serialization import convert_numpy_to_python


logger = logging.getLogger(__name__)


def create_screening_record(*, data, screening_data, user):
    """Create one screening record with JSON-safe calculated values."""
    data_converted = convert_numpy_to_python(data)
    screening_data_converted = convert_numpy_to_python(screening_data)
    try:
        return MyModel.objects.create(
            **data_converted,
            screening_data=screening_data_converted,
        )
    except Exception:
        logger.exception('Unable to create screening record for user %s', user.pk)
        raise
