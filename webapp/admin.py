from django.contrib import admin
from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from import_export.admin import ImportExportModelAdmin
from modeltranslation.admin import TranslationAdmin  # <-- ВАЖНО: Новый класс вместо Parler
from .models import *

# --- Настройки сайта (Без перевода, просто ModelAdmin) ---

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Админка для общих настроек сайта (Singleton)"""
    list_display = ('hero_title_home', 'email', 'phone')

    fieldsets = (
        ('Контактная информация', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Главная страница (Hero и О нас)', {
            'fields': ('hero_title_home', 'hero_subtitle_home', 'hero_image_home', 'about_text_intro', 'about_image')
        }),
        ('Страница "О нас" (Hero)', {
            'fields': ('hero_image_about',)
        }),
        ('Страница "Лаборатории" (Hero)', {
            'fields': ('hero_image_labs', 'hero_image_lab_detail')
        }),
        ('Страницы Проектов (Hero)', {
            'fields': ('hero_image_all_projects', 'hero_image_projects_field', 'hero_image_project_detail')
        }),
        ('Страница "Контакты" (Hero)', {
            'fields': ('contact_hero_title', 'contact_hero_subtitle', 'hero_image_contacts')
        }),
        ('Страница "Новости" и "Команда" (Hero)', {
            'fields': ('hero_image_news', 'hero_image_news_detail', 'hero_image_team_detail')
        }),
    )

    def has_add_permission(self, request):
        # Запрещаем создавать вторую настройку, если одна уже есть
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# --- Модели с ПЕРЕВОДОМ (TranslationAdmin) ---

@admin.register(MissionItem)
class MissionItemAdmin(TranslationAdmin):
    list_display = ('name', 'icon_class', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'description') # Убрали translations__
    ordering = ('order',)


@admin.register(Announcement)
class AnnouncementAdmin(TranslationAdmin):
    list_display = ('title', 'event_date')
    list_filter = ('event_date',)
    search_fields = ('title',)


@admin.register(NewsItem)
class NewsItemAdmin(TranslationAdmin):
    list_display = ('title', 'publish_date')
    search_fields = ('title', 'content')
    readonly_fields = ('slug',)
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(Partner)
class PartnerAdmin(TranslationAdmin):
    list_display = ('name', 'website_url')
    search_fields = ('name',)


# --- Участники и Руководство ---

@admin.register(Management)
class ManagementAdmin(TranslationAdmin):
    list_display = ('name', 'position', 'order', 'email')
    list_editable = ('order',)
    search_fields = ('name', 'position')

    fieldsets = (
        (None, {
            'fields': ('name', 'position', 'photo', 'biography', 'order'),
        }),
        ('Контакты и сети', {
            'fields': ('email', 'linkedin_url'),
        }),
        ('Научные ID', {
            'fields': ('orcid_id', 'scopus_id', 'publications_url'),
            'classes': ('collapse',),
        }),
    )
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(TeamMember)
class TeamMemberAdmin(TranslationAdmin):
    list_display = ('name', 'position', 'is_featured', 'email')
    list_editable = ('is_featured',)
    search_fields = ('name', 'position')

    fieldsets = (
        (None, {
            'fields': ('name', 'position', 'is_featured', 'photo', 'description'),
        }),
        ('Контакты и сети', {
            'fields': ('email', 'linkedin_url', 'twitter_url'),
        }),
        ('Научные ID', {
            'fields': ('orcid_id', 'scopus_id', 'publications_url'),
            'classes': ('collapse',),
        }),
    )
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


# --- Основные Модели (ProjectAdmin) ---

@admin.register(Project)
class ProjectAdmin(TranslationAdmin):
    list_display = ('name', 'lab', 'field', 'author_member', 'date')
    list_filter = ('lab', 'field', 'date')
    # Поиск через связанные поля теперь работает напрямую через имя поля
    search_fields = ('name', 'lab__name', 'author_member__name')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'content'),
        }),
        ('Научные детали и преимущества', {
            'fields': ('application_area', 'superiority'),
            'description': 'Подробная научная информация о проекте.',
        }),
        ('Руководство и команда', {
            'fields': ('author_member', 'author', 'team'), # Добавил author (текстовое поле) на всякий случай
        }),
        ('Связи и дата', {
            'fields': ('lab', 'field', 'date'),
        }),
        ('Детали проекта', {
            'fields': ('client_name', 'year_completed', 'technologies', 'project_url'),
        }),
        ('Медиа и документы', {
            'fields': ('main_image', 'youtube_url', 'pdf_file'),
        }),
    )
    readonly_fields = ('slug',)
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(Lab)
class LabAdmin(TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('slug',)
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(Field)
class FieldAdmin(TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('slug',)
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(SuccessFact)
class SuccessFactAdmin(TranslationAdmin):
    list_display = ('title', 'value', 'icon_class', 'order')
    list_editable = ('icon_class', 'order')
    search_fields = ('title',)
    ordering = ('order',)


# --- Модели без перевода ---

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'topic', 'email')
    search_fields = ('full_name', 'topic')
    list_per_page = 25


@admin.register(Mailing)
class MailingAdmin(ImportExportModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)