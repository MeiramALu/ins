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

    # ИСПРАВЛЕНО: slug заменен на str для поддержки кириллицы
    path('labs/<str:lab_slug>/', views.lab_detail, name='lab_detail'),

    path('how/<str:lab_slug>/<str:field_slug>/<str:project_slug>/', views.project, name='project'),

    # ИСПРАВЛЕНО: lab_slug заменен на str
    path('labs/<str:lab_slug>/all/', views.all_projects, name='all_projects'),

    # ИСПРАВЛЕНО: lab_slug и field_slug заменены на str
    path('labs/<str:lab_slug>/<str:field_slug>/', views.projects, name='projects_by_field'),

    # НОВОСТИ
    # ИСПРАВЛЕНО: news_slug заменен на str (если новости могут быть кириллическими)
    path('news/', views.news_list, name='news_list'),
    path('news/<str:news_slug>/', views.news_detail, name='news_detail'),
]