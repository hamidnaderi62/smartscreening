"""Authorized write actions for screening reports."""

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from ..models import MyModel
from ..permissions import can_view_screening


class InvalidDoctorComment(ValueError):
    """Raised when a doctor comment payload is incomplete."""


def update_doctor_comment(*, user, model_id, comment):
    """Validate authorization and persist a doctor comment."""
    if not model_id or not isinstance(comment, str) or not comment.strip():
        raise InvalidDoctorComment('Missing required fields.')

    screening = get_object_or_404(MyModel, pk=model_id)
    if not can_view_screening(user, screening.userid):
        raise PermissionDenied('You cannot update this screening report.')

    screening.doctor_comment = comment.strip()
    screening.save(update_fields=('doctor_comment', 'updated'))
    return screening
