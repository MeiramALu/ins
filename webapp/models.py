from django.db import models
from django.urls import reverse
from django.utils import timezone
from ckeditor.fields import RichTextField
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# --- Существующие модели (без изменений) ---
class Lab(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=100),
        description = models.TextField(_("Описание"))
    )
    fields = models.ManyToManyField('Field', related_name='labs', blank=True,)
    image = models.ImageField(upload_to='labs/', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True, help_text="Автоматически генерируется из названия")

    def save(self, *args, **kwargs):
        if not self.slug:
            name_ru = self.safe_translation_getter('name', language_code='ru')
            if name_ru:
                self.slug = slugify(name_ru, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('name', '---')

    def get_absolute_url(self):
        return reverse('lab', kwargs={'lab_slug': self.slug})

    class Meta:
        verbose_name = 'Лаборатория'
        verbose_name_plural = 'Лаборатории'


class Field(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=100),
        description = models.TextField(_("Описание"))
    )
    image = models.ImageField(upload_to='fields/')
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True, help_text="Автоматически генерируется из названия")

    def save(self, *args, **kwargs):
        if not self.slug:
            name_ru = self.safe_translation_getter('name', language_code='ru')
            if name_ru:
                self.slug = slugify(name_ru, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('name', '---')

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'


class Project(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=100),
        description = models.TextField(_("Описание")),
        content = RichTextField(_("Содержание"))
    )
    lab = models.ForeignKey('Lab', on_delete=models.CASCADE, related_name='projects', blank=True, null=True)
    field = models.ForeignKey('Field', on_delete=models.CASCADE, related_name='projects', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True, help_text="Автоматически генерируется из названия")
    date = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='project_pdfs/', blank=True, null=True, verbose_name="PDF Файл")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на YouTube")

    def save(self, *args, **kwargs):
        if not self.slug:
            name_ru = self.safe_translation_getter('name', language_code='ru')
            if name_ru:
                self.slug = slugify(name_ru, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('name', '---')

    def get_absolute_url(self):
        try:
            url = reverse('project',
                          kwargs={'lab_slug': self.lab.slug, 'field_slug': self.field.slug, 'project_slug': self.slug})
        except AttributeError:
            url = reverse('all-projects')
        return url

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

# --- НОВЫЕ МОДЕЛИ ---

class NewsArticle(TranslatableModel):
    """Модель для новостей"""
    translations = TranslatedFields(
        title = models.CharField(_("Заголовок"), max_length=200),
        content = RichTextField(_("Содержание")),
        excerpt = models.TextField(_("Краткое содержание"), blank=True)
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="Автоматически генерируется из заголовка")
    image = models.ImageField(_("Изображение"), upload_to='news_images/', blank=True, null=True)
    publish_date = models.DateField(_("Дата публикации"), default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            title_ru = self.safe_translation_getter('title', language_code='ru')
            if title_ru:
                self.slug = slugify(title_ru, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('title', '---')

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'news_slug': self.slug})

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-publish_date']


class Partner(TranslatableModel):
    """Модель для партнеров"""
    translations = TranslatedFields(
        name = models.CharField(_("Название партнера"), max_length=150),
    )
    logo = models.ImageField(_("Логотип"), upload_to='partner_logos/')
    website_url = models.URLField(_("Ссылка на сайт"), blank=True)

    def __str__(self):
        return self.safe_translation_getter('name', '---')

    class Meta:
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'


# --- Остальные модели (без изменений) ---
class Application(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    topic = models.CharField(max_length=50)
    message = models.CharField(max_length=500)

    def __str__(self):
        return f'{self.full_name} - {self.topic}'

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class Mailing(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class TeamMember(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_('Имя и фамилия'), max_length=100),
        position = models.CharField(_('Должность'), max_length=100),
        description = models.TextField(_('Описание'))
    )
    photo = models.ImageField(_('Фотография'), upload_to='team_photos/', blank=True, null=True)

    def __str__(self):
        return self.safe_translation_getter('name', '---')

    class Meta:
        verbose_name = 'Участник команды'
        verbose_name_plural = 'Участники команды'


class SuccessFact(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(_("Заголовок"), max_length=100),
        value = models.CharField(_("Значение"), max_length=20)
    )

    def __str__(self):
        return f"{self.safe_translation_getter('title', '---')}: {self.safe_translation_getter('value', '---')}"

    class Meta:
        verbose_name = 'Факт об успехе'
        verbose_name_plural = 'Факты об успехе'

