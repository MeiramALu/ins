from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
import random
from django.contrib import messages
from django.db.models import F
from django.utils.translation import get_language  # Для получения текущего языка
from parler.views import get_language_tabs  # Для корректной работы вкладок Parler (если используется)

# Импортируем все модели, которые используются на сайте
from .models import (
    Lab, Field, Project, TeamMember, Application,
    Mailing, SuccessFact, NewsItem, Partner,  # NewsArticle заменен на NewsItem
    SiteSettings, MissionItem, Announcement  # Добавлены новые модели
)


# --- Вспомогательная функция для получения общих данных ---
def get_common_context():
    """Получает общие данные, необходимые для многих шаблонов (например, футер)."""
    try:
        settings = SiteSettings.objects.first()
    except:
        # Заглушка, если база данных еще пуста
        settings = None

        # Получаем лаборатории для футера
    labs = Lab.objects.all()

    return {
        'settings': settings,
        'labs': labs,  # Используется в base.html (футер)
    }


# --- ОБЩИЕ СТРАНИЦЫ ---

def index(request):
    """Главная страница."""
    context = get_common_context()

    # Получаем данные для разных блоков на странице
    fields = Field.objects.all()
    best_projects = Project.objects.all().select_related('lab').order_by('-id')[:3]
    partners = Partner.objects.all()

    # Получаем Mission/Goals/Strategy
    mission_items = MissionItem.objects.all()

    # Добавляем последние новости (для блока на главной странице)
    latest_news = NewsItem.objects.order_by(F('publish_date').desc(nulls_last=True))[:2]

    # Добавляем последние объявления
    latest_announcements = Announcement.objects.order_by(F('event_date').desc(nulls_last=True))[:3]

    context.update({
        'all_fields': fields,
        'best_projects': best_projects,
        'partners': partners,
        'latest_news': latest_news,
        'mission_items': mission_items,
        'latest_announcements': latest_announcements,
    })
    return render(request, 'index.html', context)


def about(request):
    """Страница 'О нас'."""
    context = get_common_context()

    all_fields_list = list(Field.objects.all())
    sample_size = min(len(all_fields_list), 6)
    random_fields = random.sample(all_fields_list, sample_size)

    success_facts = SuccessFact.objects.all()
    team_members = TeamMember.objects.all()

    # Mission/Goals/Strategy также отображаются на странице About
    mission_items = MissionItem.objects.all()

    context.update({
        'all_fields': random_fields,
        'team_members': team_members,
        'success_facts': success_facts,
        'mission_items': mission_items,
    })
    return render(request, 'about.html', context)


def contacts(request):
    """Страница контактов."""
    context = get_common_context()
    # Данные для контактов уже в 'settings'
    return render(request, 'contacts.html', context)


def how(request):
    """Страница 'Как это работает'."""
    context = get_common_context()
    return render(request, 'how.html', context)


# --- СТРАНИЦЫ ЛАБОРАТОРИЙ ---

def lab_list(request):
    """Страница со списком ВСЕХ лабораторий."""
    context = get_common_context()

    labs = Lab.objects.all()

    context.update({
        'labs': labs,
    })
    return render(request, 'lab_list.html', context)


def lab_detail(request, lab_slug):
    """Детальная страница одной лаборатории."""
    context = get_common_context()

    lab = get_object_or_404(Lab, slug=lab_slug)
    lab_fields = lab.fields.all()

    context.update({
        'lab': lab,
        'lab_fields': lab_fields
    })
    return render(request, 'lab.html', context)


# --- СТРАНИЦЫ ПРОЕКТОВ ---

def projects(request, lab_slug, field_slug):
    """Страница проектов, отфильтрованных по лаборатории И направлению."""
    context = get_common_context()

    lab = get_object_or_404(Lab, slug=lab_slug)
    field = get_object_or_404(Field, slug=field_slug)
    projects = Project.objects.filter(lab=lab, field=field)

    context.update({
        'projects': projects,
        'lab': lab,
        'field': field,
    })
    return render(request, 'projects.html', context)


def all_projects(request, lab_slug):
    """Страница всех проектов одной лаборатории."""
    context = get_common_context()

    lab = get_object_or_404(Lab, slug=lab_slug)
    projects = Project.objects.filter(lab=lab)

    context.update({
        'projects': projects,
        'lab': lab,
    })
    return render(request, 'all_projects.html', context)


def project(request, lab_slug, field_slug, project_slug):
    """Детальная страница одного проекта."""
    context = get_common_context()

    project = get_object_or_404(Project, slug=project_slug, lab__slug=lab_slug, field__slug=field_slug)

    related_projects = Project.objects.filter(lab=project.lab).exclude(slug=project.slug)[:4]

    context.update({
        'project': project,
        'related_projects': related_projects,
    })
    return render(request, 'project.html', context)


# --- СТРАНИЦЫ НОВОСТЕЙ ---

def news_list(request):
    """Страница со списком всех новостей."""
    context = get_common_context()

    news = NewsItem.objects.all().order_by(F('publish_date').desc(nulls_last=True))  # NewsArticle заменен на NewsItem

    context.update({
        'news_list': news,
    })
    return render(request, 'news_list.html', context)


def news_detail(request, news_slug):
    """Страница с детальной информацией о новости."""
    context = get_common_context()

    news_item = get_object_or_404(NewsItem, slug=news_slug)  # NewsArticle заменен на NewsItem

    context.update({
        'news_item': news_item,
    })
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