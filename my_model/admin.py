from django.contrib import admin
from .models import MyModel,AssessmentGroup,Assessment


admin.site.register(AssessmentGroup)
admin.site.register(Assessment)
admin.site.register(MyModel)
