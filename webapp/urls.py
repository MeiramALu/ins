from django.urls import path
from . import views

urlpatterns = [
    # ОБЩИЕ СТРАНИЦЫ
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('how/', views.how, name='how'),

    # ФОРМЫ
    path('form/contact/', views.contact_form, name='contact_form'),
    path('form/mailing/', views.mailing_form, name='mailing_form'),

    # ЛАБОРАТОРИИ
    path('labs/', views.lab_list, name='lab_list'),
    path('labs/<str:lab_slug>/', views.lab_detail, name='lab_detail'),

    # ДЕТАЛЬНЫЕ СТРАНИЦЫ УЧАСТНИКОВ
    path('team/member/<int:pk>/', views.team_member_detail, name='team_member_detail'),

    # --- ПРОЕКТЫ ---

    # 1. Общее портфолио (Все проекты)
    path('portfolio/', views.global_portfolio, name='global_portfolio'),

    # 2. НОВЫЙ ПУТЬ: Детальная страница независимого проекта (без Лаборатории)
    path('project/<str:project_slug>/', views.project_detail_independent, name='project_independent'),

    # 3. Проекты внутри лабораторий
    path('labs/<str:lab_slug>/all/', views.all_projects, name='all_projects'),
    path('labs/<str:lab_slug>/<str:field_slug>/', views.projects, name='projects_by_field'),

    # Детальная страница проекта внутри лаборатории
    path('labs/<str:lab_slug>/<str:field_slug>/<str:project_slug>/', views.project, name='project'),

    # НОВОСТИ
    path('news/', views.news_all, name='news_all'),
    path('news/<str:news_slug>/', views.news_detail, name='news_detail'),

    path('api/chat/', views.chat_api, name='chat_api'),

]