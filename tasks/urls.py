from django.urls import path
from . import views

urlpatterns = [
    path('', views.tasks, name='tasks'),  # Página principal de tareas
    path('completed/', views.tasks_completed, name='tasks_completed'),  # Tareas completadas
    path('create/', views.create_task, name='create_task'),  # Crear una tarea
    path('<int:task_id>/', views.task_detail, name='task_detail'),  # Detalle de tarea específica
    path('<int:task_id>/complete', views.complete_task, name='complete_task'),  # Completar tarea
    path('<int:task_id>/delete', views.delete_task, name='delete_task'),  # Eliminar tarea
]
