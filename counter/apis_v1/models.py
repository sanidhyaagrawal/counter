from django.db import models

# Create your models here.

class Results(models.Model):
    count = models.IntegerField()
    img = models.ImageField(upload_to='results/')
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.count}"