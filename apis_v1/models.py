from django.db import models

class InfrenceModels(models.Model):
    model_name = models.CharField(max_length=100)
    file = models.FileField(upload_to='models/', null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.model_name}"