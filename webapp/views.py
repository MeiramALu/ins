from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
import random
from django.contrib import messages
from django.db.models import F  # Для упорядочивания по полю в NewsArticle

# Импортируем все модели, которые используются на сайте
from .models import (
    Lab, Field, Project, TeamMember, Application,
    Mailing, SuccessFact, NewsArticle, Partner
)


# --- ОБЩИЕ СТРАНИЦЫ ---

def index(request):
    """Главная страница."""
    # Получаем данные для разных блоков на странице
    fields = Field.objects.all()
    # Выбираем 3 лучших/последних проекта
    best_projects = Project.objects.all().select_related('lab').order_by('-id')[:3]
    partners = Partner.objects.all()

    # Добавляем последние новости (для блока на главной странице)
    latest_news = NewsArticle.objects.order_by(F('published_date').desc(nulls_last=True))[:2]

    context = {
        'all_fields': fields,
        'best_projects': best_projects,
        'partners': partners,
        'latest_news': latest_news,
    }
    return render(request, 'index.html', context)


def about(request):
    """Страница 'О нас'."""
    all_fields_list = list(Field.objects.all())
    sample_size = min(len(all_fields_list), 6)
    random_fields = random.sample(all_fields_list, sample_size)

    success_facts = SuccessFact.objects.all()
    team_members = TeamMember.objects.all()

    context = {
        'all_fields': random_fields,
        'team_members': team_members,
        'success_facts': success_facts,
    }
    return render(request, 'about.html', context)


def contacts(request):
    """Страница контактов."""
    return render(request, 'contacts.html')


def how(request):
    """Страница 'Как это работает'."""
    return render(request, 'how.html')


# --- СТРАНИЦЫ ЛАБОРАТОРИЙ ---

def lab_list(request):
    """Страница со списком ВСЕХ лабораторий."""
    labs = Lab.objects.all()
    context = {
        'labs': labs,
    }
    return render(request, 'lab_list.html', context)


def lab_detail(request, lab_slug):
    """Детальная страница одной лаборатории."""
    lab = get_object_or_404(Lab, slug=lab_slug)
    lab_fields = lab.fields.all()
    context = {
        'lab': lab,
        'lab_fields': lab_fields
    }
    return render(request, 'lab.html', context)


# --- СТРАНИЦЫ ПРОЕКТОВ ---

def projects(request, lab_slug, field_slug):
    """Страница проектов, отфильтрованных по лаборатории И направлению."""
    lab = get_object_or_404(Lab, slug=lab_slug)
    field = get_object_or_404(Field, slug=field_slug)
    projects = Project.objects.filter(lab=lab, field=field)
    context = {
        'projects': projects,
        'lab': lab,
        'field': field,
    }
    return render(request, 'projects.html', context)


def all_projects(request, lab_slug):
    """Страница всех проектов одной лаборатории."""
    lab = get_object_or_404(Lab, slug=lab_slug)
    projects = Project.objects.filter(lab=lab)
    context = {
        'projects': projects,
        'lab': lab,
    }
    return render(request, 'all_projects.html', context)


def project(request, lab_slug, field_slug, project_slug):
    """Детальная страница одного проекта (ранее project_detail)."""
    project = get_object_or_404(Project, slug=project_slug, lab__slug=lab_slug, field__slug=field_slug)
    context = {
        'project': project,
    }
    return render(request, 'project.html', context)


# --- СТРАНИЦЫ НОВОСТЕЙ ---

def news_list(request):
    """Страница со списком всех новостей."""
    news = NewsArticle.objects.all().order_by(F('published_date').desc(nulls_last=True))
    context = {
        'news_list': news,
    }
    return render(request, 'news_list.html', context)


def news_detail(request, news_slug):
    """Страница с детальной информацией о новости."""
    news_item = get_object_or_404(NewsArticle, slug=news_slug)
    context = {
        'news_item': news_item,
    }
    return render(request, 'news_detail.html', context)


# --- ОБРАБОТЧИКИ ФОРМ ---

def contact_form(request):
    """Обработчик формы обратной связи."""
    if request.method == 'POST':
        Application.objects.create(
            full_name=request.POST.get('fullname', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            topic=request.POST.get('subject', ''),
            message=request.POST.get('message', '')
        )
        messages.success(request, 'Спасибо! Ваша заявка принята.')
    return redirect('contacts')


def mailing_form(request):
    """Обработчик формы подписки на рассылку."""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if not Mailing.objects.filter(email=email).exists():
                Mailing.objects.create(email=email)
                messages.success(request, 'Спасибо! Вы успешно подписались на рассылку.')
            else:
                messages.info(request, 'Этот email уже подписан на рассылку.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))