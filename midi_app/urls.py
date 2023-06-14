from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_midi, name='upload_midi'),
]