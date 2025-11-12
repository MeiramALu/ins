from django.contrib import admin
from .models import *
from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from import_export.admin import ImportExportModelAdmin
from parler.admin import TranslatableAdmin

# --- Регистрация новых моделей ---

@admin.register(NewsArticle)
class NewsArticleAdmin(TranslatableAdmin):
    list_display = ('title', 'publish_date')
    search_fields = ('translations__title',)
    readonly_fields = ('slug',) # slug генерируется автоматически
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget},
    }

@admin.register(Partner)
class PartnerAdmin(TranslatableAdmin):
    list_display = ('name', 'website_url')
    search_fields = ('translations__name',)

# --- Существующие классы (без изменений) ---

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
    list_display = ('title', 'value')
    search_fields = ('translations__title',)

