from django.urls import path
from .import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/update/', views.project_update, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:project_id>/task/add/', views.task_create, name='task_create'),
    path('task/<int:pk>/update/', views.task_update, name='task_update'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('member/<int:pk>/remove/', views.remove_member, name='remove_member'),
    path('project/<int:pk>/add-member/', views.add_project_member, name='add_project_member'),
    path('task/<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),
    path('task/<int:task_id>/comment/', views.add_comment, name='add_comment'),
    path('task/<int:task_id>/comment/', views.add_comment, name='add_comment'),
    path('notification/read/<int:pk>/', views.mark_as_read, name='mark_as_read'), 
]



