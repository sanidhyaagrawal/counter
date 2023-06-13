#django imports
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token 

#project imports
from apis_v1 import views

urlpatterns = [
    path('inference', views.inference, name='inference'),
]
