from django.db import models

class Pedigree(models.Model):
    code = models.CharField(max_length=50, unique=True)
    famid = models.CharField(max_length=50)
    pedigree_data = models.JSONField()
    risk_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.famid}"