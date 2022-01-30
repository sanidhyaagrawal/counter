from django.db import models

# Create your models here.

class Results(models.Model):
    count = models.IntegerField()
    image = models.ImageField(upload_to='images/', null=True)
    output = models.ImageField(upload_to='results/', null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.count}"

class InfrenceModels(models.Model):
    model_name = models.CharField(max_length=100)
    file = models.FileField(upload_to='models/', null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.model_name}"