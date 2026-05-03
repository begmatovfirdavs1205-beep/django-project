from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quiz/<int:subject_id>/', views.quiz_view, name='quiz'),
    path('api/quiz/<int:subject_id>/submit/', views.submit_quiz_api, name='submit_quiz_api'),
    path('api/ai-helper/', views.ai_helper_api, name='ai_helper_api'),
    path('api/subjects/', views.subjects_api, name='subjects_api'),
    path('api/stats/', views.stats_api, name='stats_api'),
]
