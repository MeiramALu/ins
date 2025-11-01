# C:\Users\Meiram\PycharmProjects\ins\webapp\urls.py

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
    path('labs/<slug:lab_slug>/', views.lab_detail, name='lab_detail'),

    # ПРОЕКТЫ
    # URL, который вызывал ошибку, теперь использует views.project
    path('how/<slug:lab_slug>/<slug:field_slug>/<slug:project_slug>/', views.project, name='project'),

    path('labs/<slug:lab_slug>/all/', views.all_projects, name='all_projects'),
    path('labs/<slug:lab_slug>/<slug:field_slug>/', views.projects, name='projects_by_field'),

    # НОВОСТИ
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:news_slug>/', views.news_detail, name='news_detail'),
]