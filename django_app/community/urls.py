from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/vote/', views.vote_post, name='vote_post'),
    path('post/<int:post_id>/report/', views.report_post, name='report_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]
