from django.db import models
from django.contrib.auth.models import User


class ECGClassification(models.Model):
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, null=True, blank=True)
    image_input = models.ImageField(upload_to='images/ecg_classification', null=True, blank=True)
    prediction_value = models.FloatField(null=True, blank=True)
    prediction_class = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.prediction_class}"

