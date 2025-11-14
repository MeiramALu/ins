from django.http import HttpResponseRedirect, Http404, JsonResponse  # <-- Добавил JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt  # <-- Добавил
from django.views.decorators.http import require_POST # <-- Добавил
import random
import json  # <-- Добавил
import markdown
from django.contrib import messages
from django.db.models import F
from .ai_assistant import ask_gemini
from .models import (
    Lab, Field, Project, TeamMember, Application,
    Mailing, SuccessFact, NewsItem, Partner,
    SiteSettings, MissionItem, Announcement, Management
)


# --- Вспомогательная функция ---
def get_common_context():
    """
    Возвращает контекст, который нужен на каждой странице (например, для футера).
    """
    settings = SiteSettings.objects.first()
    labs = Lab.objects.all()
    return {
        'settings': settings,
        'labs': labs,
    }


# --- ОБЩИЕ СТРАНИЦЫ ---

def index(request):
    """Главная страница."""
    context = get_common_context()

    fields = Field.objects.all()
    # Лучшие 3 проекта (последние добавленные)
    best_projects = Project.objects.all().select_related('lab').order_by('-id')[:3]
    partners = Partner.objects.all()
    mission_items = MissionItem.objects.all()

    # Последние 3 новости
    latest_news = NewsItem.objects.order_by(F('publish_date').desc(nulls_last=True))[:3]
    # Последние 4 объявления
    latest_announcements = Announcement.objects.order_by(F('event_date').desc(nulls_last=True))[:4]

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

    # 1. Секция направлений (берем случайные Лаборатории для разнообразия или все)
    all_labs_list = list(Lab.objects.all())
    # Если лабораторий больше 6, берем 6 случайных, иначе все
    sample_size = min(len(all_labs_list), 6)
    labs_for_display = random.sample(all_labs_list, sample_size)

    # 2. Контент страницы
    success_facts = SuccessFact.objects.all()
    mission_items = MissionItem.objects.all()

    # ВАЖНО: Добавили партнеров, чтобы блок внизу не был пустым
    partners = Partner.objects.all()

    # 3. КОМАНДА: Показываем только тех, у кого в админке стоит галочка "Показывать в О нас"
    team_members = TeamMember.objects.filter(is_featured=True)

    # 4. РУКОВОДСТВО: Сортируем по полю order (1, 2, 3...)
    management_members = Management.objects.all().order_by('order')

    context.update({
        'all_fields': labs_for_display,  # Используется в слайдере "Направления"
        'team_members': team_members,  # Избранные сотрудники
        'success_facts': success_facts,
        'mission_items': mission_items,
        'management_members': management_members,
        'partners': partners,  # Партнеры (логотипы)
    })
    return render(request, 'about.html', context)


def contacts(request):
    """Страница контактов."""
    context = get_common_context()
    return render(request, 'contacts.html', context)


def how(request):
    """Страница 'Как это работает' (или список всех Лабораторий)."""
    context = get_common_context()
    context['labs'] = Lab.objects.all()
    return render(request, 'how.html', context)


# --- СТРАНИЦЫ ЛАБОРАТОРИЙ ---

def lab_list(request):
    """Список всех лабораторий (альтернативный вид)."""
    context = get_common_context()
    labs = Lab.objects.all()
    context.update({'labs': labs})
    return render(request, 'lab_list.html', context)


def lab_detail(request, lab_slug):
    """Детальная страница лаборатории."""
    context = get_common_context()
    lab = get_object_or_404(Lab, slug=lab_slug)
    lab_fields = lab.fields.all()
    context.update({'lab': lab, 'lab_fields': lab_fields})
    return render(request, 'lab.html', context)


# --- СТРАНИЦЫ ПРОЕКТОВ ---

def projects(request, lab_slug, field_slug):
    """Список проектов, отфильтрованных по Лаборатории И Направлению."""
    context = get_common_context()
    lab = get_object_or_404(Lab, slug=lab_slug)
    field = get_object_or_404(Field, slug=field_slug)
    projects = Project.objects.filter(lab=lab, field=field)
    context.update({'projects': projects, 'lab': lab, 'field': field})
    return render(request, 'projects.html', context)


def all_projects(request, lab_slug):
    """Все проекты конкретной лаборатории."""
    context = get_common_context()
    lab = get_object_or_404(Lab, slug=lab_slug)
    projects = Project.objects.filter(lab=lab)
    context.update({'projects': projects, 'lab': lab})
    return render(request, 'all_projects.html', context)


def project(request, lab_slug, field_slug, project_slug):
    """Детальная страница проекта (ПРИВЯЗАННОГО К ЛАБОРАТОРИИ)."""
    context = get_common_context()
    # Ищем проект, который принадлежит указанной лабе и направлению
    project = get_object_or_404(Project, slug=project_slug, lab__slug=lab_slug, field__slug=field_slug)

    # Похожие проекты (той же лаборатории, кроме текущего)
    related_projects = Project.objects.filter(lab=project.lab).exclude(slug=project.slug)[:4]

    # Команда этого проекта
    project_team = project.team.all()

    context.update({
        'project': project,
        'related_projects': related_projects,
        'project_team': project_team,
    })
    return render(request, 'project.html', context)


def project_detail_independent(request, project_slug):
    """
    Детальная страница НЕЗАВИСИМОГО проекта (без лаборатории).
    """
    context = get_common_context()

    # Ищем проект просто по slug (без привязки к лабе)
    project = get_object_or_404(Project, slug=project_slug)

    project_team = project.team.all()

    # Похожие проекты (просто последние добавленные, так как лабы нет)
    related_projects = Project.objects.exclude(slug=project.slug).order_by('-date')[:3]

    context.update({
        'project': project,
        'project_team': project_team,
        'related_projects': related_projects,
    })
    return render(request, 'project.html', context)


def global_portfolio(request):
    """Страница со ВСЕМИ проектами (и от лабораторий, и отдельные)."""
    context = get_common_context()

    all_projects = Project.objects.all().order_by('-date')

    context.update({
        'projects': all_projects,
    })
    return render(request, 'portfolio.html', context)


# --- СТРАНИЦЫ НОВОСТЕЙ ---

def news_all(request):
    """Страница всех новостей."""
    context = get_common_context()
    all_news = NewsItem.objects.all().order_by(F('publish_date').desc(nulls_last=True))
    context.update({'all_news': all_news})
    return render(request, 'news_all.html', context)


def news_detail(request, news_slug):
    """Детальная страница новости."""
    context = get_common_context()
    news_item = get_object_or_404(NewsItem, slug=news_slug)
    context.update({'news_item': news_item})
    return render(request, 'news_detail.html', context)


# --- ОБРАБОТЧИКИ ФОРМ (POST) ---

def contact_form(request):
    """Обработка формы 'Оставить заявку'."""
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
    """Обработка формы подписки на рассылку."""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if not Mailing.objects.filter(email=email).exists():
                Mailing.objects.create(email=email)
                messages.success(request, 'Спасибо! Вы успешно подписались на рассылку.')
            else:
                messages.info(request, 'Этот email уже подписан на рассылку.')
    # Возвращает пользователя на ту же страницу, откуда пришел запрос
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def team_member_detail(request, pk):
    """
    Детальная страница сотрудника.
    """
    context = get_common_context()
    member = None
    is_management = False

    try:
        # Сначала ищем в таблице Руководства
        member = Management.objects.get(pk=pk)
        is_management = True
    except Management.DoesNotExist:
        try:
            # Если не нашли, ищем в таблице Команды
            member = get_object_or_404(TeamMember, pk=pk)
            is_management = False
        except TeamMember.DoesNotExist:
            raise Http404("Член команды не найден.")

    context.update({
        'member': member,
        'is_management': is_management
    })
    return render(request, 'team_member_detail.html', context)


# --- API GEMINI ---

@csrf_exempt
@require_POST
def chat_api(request):
    """API для общения с Gemini через AJAX"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Спрашиваем Gemini (функция из ai_assistant.py)
        ai_response = ask_gemini(user_message)

        # Преобразуем Markdown в HTML
        html_response = markdown.markdown(ai_response)

        return JsonResponse({'response': html_response})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)