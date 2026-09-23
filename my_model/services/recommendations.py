"""Optional external recommendations used by screening detail pages."""

import logging

import requests


logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 5


def _get_json(url, *, params):
    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json() if response.content else []
    except (requests.RequestException, ValueError):
        logger.warning("SmartLife recommendations unavailable: %s", url)
        return []


def get_related_resources(base_url, *, tags, speciality):
    """Return related content and doctors without blocking the report page."""
    base_url = base_url.rstrip('/')
    related_contents = _get_json(
        f'{base_url}/filter_content_list',
        params={'q': tags},
    )
    related_doctors = _get_json(
        f'{base_url}/doctor/filter_doctor_list',
        params={'q': speciality},
    )
    return related_contents, related_doctors
