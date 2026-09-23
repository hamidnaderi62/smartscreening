# views.py
from django.http import Http404, JsonResponse, HttpResponse
import json

from django.shortcuts import render, redirect
from .models import MyModel
from .forms import AssessmentSelectionForm
from django.views.decorators.http import require_POST
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from account.models import Profile
from .assessment_catalog import ASSESSMENTS, get_assessment_or_404
from .permissions import can_view_screening
from .services.calculation_inputs import validate_calculation_input
from .services.assessment_calculations import calculate_selected_assessments
from .services.result_formatting import build_result_context
from .services.persistence import create_screening_record
from .services.pdf_reports import generate_screening_pdf
from .services.report_actions import InvalidDoctorComment, update_doctor_comment
from .services.localization import (
    language_for_request,
    localize_assessments,
    localized_reverse,
    normalize_language,
)
from .services.screening_data import collect_screening_data as build_screening_data
import logging

logger = logging.getLogger(__name__)
assessments = ASSESSMENTS


@login_required
def screening_list(request):
    language = normalize_language(language_for_request(request))
    return _localized_screening_list(request, language)


@login_required
def screening_list_fa(request):
    return _localized_screening_list(request, 'fa')


@login_required
def screening_list_en(request):
    return _localized_screening_list(request, 'en')


@login_required
def screening_list_ar(request):
    return _localized_screening_list(request, 'ar')


def _localized_screening_list(request, language):
    return render(request, 'screening_list.html', {
        'assessments': localize_assessments(assessments, language),
        'base_template': 'base_raw.html',
    })


def _question_view(request, *, language, redirect_name):
    language = normalize_language(language)
    screening_list_url = localized_reverse('my_model:screening_list', language)
    form = AssessmentSelectionForm(
        request.POST or None,
        allowed_assessments=assessments,
    )
    if request.method == 'POST' and form.is_valid():
        selected_assessments = form.cleaned_data['selected_assessments']
        request.session['selected_assessments'] = selected_assessments
        return render(request, 'my_model.html', {
            'base_template': 'base_raw.html',
            'questionnaire_language': language,
            'selected_assessments': selected_assessments,
        })
    if request.method == 'POST':
        return render(request, 'my_model.html', {
            'base_template': 'base_raw.html',
            'questionnaire_language': language,
            'selected_assessments': [],
        })
    return redirect(screening_list_url)


@login_required
def question(request):
    """Render the shared questionnaire using the active language."""
    return _question_view(
        request,
        language=language_for_request(request),
        redirect_name='my_model:screening_list',
    )


@login_required
def question_fa(request):
    return _question_view(
        request,
        language='fa',
        redirect_name='my_model:screening_list_fa',
    )


@login_required
def question_en(request):
    return _question_view(
        request,
        language='en',
        redirect_name='my_model:screening_list_en',
    )


@login_required
def question_ar(request):
    return _question_view(
        request,
        language='ar',
        redirect_name='my_model:screening_list_ar',
    )


def _can_view_screening_user(request, target_user):
    return can_view_screening(request.user, target_user)


def collect_screening_data(request, selected_assessments, data):
    """Compatibility wrapper for the screening snapshot service."""
    return build_screening_data(selected_assessments, data)


@login_required
@require_POST
def calculate_my_model(request):
    """Validate the request boundary before running the screening calculations."""
    try:
        return _calculate_my_model(request)
    except (TypeError, ValueError, KeyError):
        logger.warning(
            'Invalid screening input for user %s',
            request.user.pk,
        )
        if getattr(getattr(request, 'resolver_match', None), 'url_name', '') == 'calculate':
            return redirect('my_model:question')
        lang = normalize_language(request.POST.get('lang'))
        return redirect(localized_reverse('my_model:question', lang))


def _calculate_my_model(request):
    data = {}
    selected_assessments = request.session.get('selected_assessments', [])
    post_data = validate_calculation_input(request.POST, selected_assessments)
    lang = normalize_language(getattr(request, 'LANGUAGE_CODE', None) or post_data.get('lang'))

    # Demographic Info
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'code': str(request.user.pk)},
    )
    if not profile.code:
        profile.code = str(request.user.pk)
        profile.save(update_fields=('code',))
    code = profile.code
    gender = 'Male'
    age = float(post_data.get('age'))
    weight = float(post_data.get('weight'))
    height = float(post_data.get('height'))
    waist_size = float(post_data.get('waist_size'))
    ethnicity = int(post_data.get('ethnicity'))
    born_place = post_data.get('born_place')
    education = float(post_data.get('education'))
    blood_group = post_data.get('blood_group')

    demographic_fields = {
        'userid': request.user,
        'code': code,
        'gender': gender,
        'age': age,
        'weight': weight,
        'height': height,
        'waist_size': waist_size,
        'ethnicity': ethnicity,
        'born_place': born_place,
        'education': education,
        'blood_group': blood_group,
    }
    data.update(demographic_fields)

    # Life Style
    activity = float(post_data.get('activity'))
    smoking = float(post_data.get('smoking'))
    alcohol = float(post_data.get('alcohol'))
    meat = float(post_data.get('meat'))
    cereal = post_data.get('cereal')
    vegetables = post_data.get('vegetables')
    dairy = float(post_data.get('dairy'))
    multivitamin = post_data.get('multivitamin')

    lifestyle_fields = {
        'activity': activity,
        'smoking': smoking,
        'alcohol': alcohol,
        'meat': meat,
        'cereal': cereal,
        'vegetables': vegetables,
        'dairy': dairy,
        'multivitamin': multivitamin,
    }
    data.update(lifestyle_fields)

    # Medical
    blood_pressure = post_data.get('blood_pressure')
    blood_glucose = post_data.get('blood_glucose')
    totchol = float(post_data.get('totchol'))
    previous_cancer = post_data.get('previous_cancer')

    medical_fields = {
        'blood_pressure': blood_pressure,
        'blood_glucose': blood_glucose,
        'totchol': totchol,
        'previous_cancer': previous_cancer,
    }
    data.update(medical_fields)

    calculate_selected_assessments(post_data, selected_assessments, data)
    # Set selected assessments IDs
    list_selected_assessments_id = [item['id'] for item in selected_assessments]
    data['selected_assessments_id'] = ', '.join(map(str, list_selected_assessments_id))

    context = build_result_context(selected_assessments, data)
    # Collect screening data and convert to JSON string
    screening_data = collect_screening_data(request, selected_assessments, data)

    my_model_instance = create_screening_record(
        data=data,
        screening_data=screening_data,
        user=request.user,
    )
    try:
        from followup.services import schedule_follow_up_for_screening

        schedule_follow_up_for_screening(
            my_model_instance,
            selected_assessments=selected_assessments,
            language=lang,
        )
    except Exception:
        # A follow-up/SMS configuration problem must not discard a valid screening.
        logger.exception('Unable to schedule follow-up for screening %s', my_model_instance.pk)

    context['selected_assessments'] = localize_assessments(selected_assessments, lang)
    context['base_template'] = 'base_raw.html'
    context['my_model_instance'] = my_model_instance
    context['code'] = code
    context['gender'] = gender
    context['age'] = int(age)

    return render(request, 'dashboard.html', context)


@login_required
@require_POST
def save_doctor_comment(request):
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise InvalidDoctorComment('Invalid JSON object.')
        update_doctor_comment(
            user=request.user,
            model_id=data.get('my_model_id'),
            comment=data.get('doctor_comment'),
        )

        return JsonResponse({'status': 'success', 'message': 'Comment saved successfully'})

    except (InvalidDoctorComment, TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON payload'}, status=400)


@login_required
def download_pdf_report(request, model_id=None):
    """Download PDF report for a specific screening record"""
    try:
        if model_id:
            my_model_instance = get_object_or_404(MyModel, id=model_id)
            if not _can_view_screening_user(request, my_model_instance.userid):
                raise PermissionDenied('You cannot download this screening report.')
        else:
            my_model_instance = MyModel.objects.filter(userid=request.user).order_by('-created').first()
            if my_model_instance is None:
                raise PermissionDenied('No screening report is available.')

        pdf_buffer, filename = generate_screening_pdf(
            my_model_instance,
            assessments,
            request,
        )

        response = FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=filename,
            content_type='application/pdf'
        )
        return response

    except (Http404, PermissionDenied):
        raise
    except ValueError:
        logger.warning('Invalid screening report data for PDF: %s', model_id)
        return HttpResponse('Invalid report data', status=400)
    except Exception:
        logger.exception('Unable to generate screening PDF for %s', model_id)
        return HttpResponse('Unable to generate report', status=500)
