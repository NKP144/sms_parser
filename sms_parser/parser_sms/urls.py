from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', index, name='home_page'),             # http://127.0.0.1:8000/
]
