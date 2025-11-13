from django.contrib import admin
from .models import *
from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from import_export.admin import ImportExportModelAdmin
from parler.admin import TranslatableAdmin


# --- Новые классы для управления контентом ---

class SiteSettingsAdmin(admin.ModelAdmin):
    """Админка для общих настроек сайта (Singleton)"""
    list_display = ('hero_title_home', 'email', 'phone')
    fieldsets = (
        ('Контактная информация', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Главная страница', {
            'fields': ('hero_title_home', 'hero_subtitle_home', 'about_text_intro', 'about_image')
        }),
        ('Страница Контактов', {
            'fields': ('contact_hero_title', 'contact_hero_subtitle')
        }),

    )

    # Singleton: разрешаем только изменение, запрещаем добавление/удаление
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MissionItem)
class MissionItemAdmin(TranslatableAdmin):
    """Админка для Миссия/Цели/Стратегия"""
    list_display = ('name', 'icon_class', 'order')
    list_editable = ('order',)
    search_fields = ('translations__name',)
    ordering = ('order',)


@admin.register(Announcement)
class AnnouncementAdmin(TranslatableAdmin):
    """Админка для Объявлений"""
    list_display = ('title', 'event_date')
    list_filter = ('event_date',)
    search_fields = ('translations__title',)


# --- Регистрация новых моделей ---

# Регистрируем SiteSettings (без декоратора, так как нужен кастомный класс)
admin.site.register(SiteSettings, SiteSettingsAdmin)


@admin.register(NewsItem) # ИСПРАВЛЕНО
class NewsItemAdmin(TranslatableAdmin): # Переименовано для соответствия модели
    list_display = ('title', 'publish_date')
    search_fields = ('translations__title',)
    readonly_fields = ('slug',)
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(Partner)
class PartnerAdmin(TranslatableAdmin):
    list_display = ('name', 'website_url')
    search_fields = ('translations__name',)


# --- Существующие классы ---

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'topic', 'email')
    search_fields = ('full_name', 'topic')
    list_per_page = 25


@admin.register(Mailing)
class MailingAdmin(ImportExportModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)


@admin.register(Lab)
class LabAdmin(TranslatableAdmin):
    list_display = ('name',)
    search_fields = ('translations__name',)
    readonly_fields = ('slug',)
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(Project)
class ProjectAdmin(TranslatableAdmin):
    list_display = ('name', 'lab', 'field', 'date')
    list_filter = ('lab', 'field', 'date')
    search_fields = ('translations__name', 'lab__translations__name')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'content'),
        }),
        ('Связи и дата', {
            'fields': ('lab', 'field', 'date'),
        }),
        ('Детали проекта', {
            'fields': ('client_name', 'year_completed', 'technologies', 'project_url'),
        }),
        ('Медиа и документы', {
            'fields': ( #'main_image', #
                'youtube_url', 'pdf_file'),
        }),
    )
    readonly_fields = ('slug',)
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(Field)
class FieldAdmin(TranslatableAdmin):
    list_display = ('name',)
    search_fields = ('translations__name',)
    readonly_fields = ('slug',)
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(TeamMember)
class TeamMemberAdmin(TranslatableAdmin):
    list_display = ('name', 'position')
    search_fields = ('translations__name', 'translations__position')
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }


@admin.register(SuccessFact)
class SuccessFactAdmin(TranslatableAdmin):
    # Добавлены новые поля
    list_display = ('title', 'value', 'icon_class', 'order')
    list_editable = ('order', 'icon_class')
    search_fields = ('translations__title',)
    ordering = ('order',)