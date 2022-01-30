from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Results

class ResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = '__all__'