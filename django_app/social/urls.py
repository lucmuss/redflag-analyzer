from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('share/create/<int:analysis_id>/', views.create_share, name='create_share'),
    path('share/<uuid:uuid>/', views.share_detail, name='share_detail'),
    path('share/delete/<uuid:uuid>/', views.delete_share, name='delete_share'),
    path('my-shares/', views.my_shares, name='my_shares'),
]
