# webapp/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import (
    Lab, Field, Project, MissionItem, NewsItem,
    Announcement, Partner, Management, TeamMember, SuccessFact
)

# --- Основные модели ---

@register(Lab)
class LabTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)

@register(Field)
class FieldTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)

@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'content', 'application_area', 'superiority', 'client_name', 'technologies', 'author')

# --- Контент сайта ---

@register(MissionItem)
class MissionTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)

@register(NewsItem)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'excerpt',)

@register(Announcement)
class AnnouncementTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(Partner)
class PartnerTranslationOptions(TranslationOptions):
    fields = ('name',)

# --- Люди ---

@register(Management)
class ManagementTranslationOptions(TranslationOptions):
    fields = ('name', 'position', 'biography',)

@register(TeamMember)
class TeamTranslationOptions(TranslationOptions):
    fields = ('name', 'position', 'description',)

@register(SuccessFact)
class SuccessFactTranslationOptions(TranslationOptions):
    fields = ('title', 'value', 'long_description',)