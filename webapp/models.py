from django.db import models
from django.urls import reverse
from django.utils import timezone
from ckeditor.fields import RichTextField
from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


# --- 1. Основные Модели (Lab, Field, Project) ---

class Lab(TranslatableModel):
    """Модель для Лабораторий"""
    translations = TranslatedFields(
        name=models.CharField(_("Название"), max_length=100),
        description=models.TextField(_("Описание"))
    )
    fields = models.ManyToManyField('Field', related_name='labs', blank=True, )
    image = models.ImageField(upload_to='labs/', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True,
                            help_text="Автоматически генерируется из названия")

    def save(self, *args, **kwargs):
        if not self.slug:
            name_ru = self.safe_translation_getter('name', language_code='ru')
            if name_ru:
                self.slug = slugify(name_ru, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('name', '---')

    def get_absolute_url(self):
        # Используем name='lab_detail' из urls.py
        return reverse('lab_detail', kwargs={'lab_slug': self.slug})

    class Meta:
        verbose_name = 'Лаборатория'
        verbose_name_plural = 'Лаборатории'


class Field(TranslatableModel):
    """Модель для Направлений/Услуг"""
    translations = TranslatedFields(
        name=models.CharField(_("Название"), max_length=100),
        description=models.TextField(_("Описание"))
    )
    image = models.ImageField(upload_to='fields/')
    hero_image = models.ImageField(_("Фоновое изображение Hero"), upload_to='field_heroes/', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True,
                            help_text="Автоматически генерируется из названия")

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
    """Модель для Проектов"""
    translations = TranslatedFields(
        name=models.CharField(_("Название"), max_length=100),
        description=models.TextField(_("Описание")),
        content=RichTextField(_("Содержание"))
    )
    lab = models.ForeignKey('Lab', on_delete=models.SET_NULL, related_name='projects', blank=True, null=True)
    field = models.ForeignKey('Field', on_delete=models.SET_NULL, related_name='projects', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True,
                            help_text="Автоматически генерируется из названия")
    date = models.DateField(default=timezone.now)
    project_url = models.URLField(_("Ссылка на проект (если опубликован)"), blank=True, null=True)
    client_name = models.CharField(_("Заказчик / Клиент"), max_length=100, blank=True, null=True)
    year_completed = models.CharField(_("Год завершения"), max_length=4, blank=True, null=True)
    technologies = models.CharField(_("Использованные технологии (перечислить через запятую)"), max_length=255,
                                    blank=True, null=True)
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
        # Более безопасная логика для получения URL проекта
        try:
            if self.lab and self.field:
                return reverse('project',
                              kwargs={'lab_slug': self.lab.slug, 'field_slug': self.field.slug, 'project_slug': self.slug})
            elif self.lab:
                 return reverse('all_projects', kwargs={'lab_slug': self.lab.slug})
            else:
                # Безопасный возврат, если нет ссылок на lab/field
                return reverse('lab_list')
        except Exception:
            # Fallback на список лабораторий, если URL не найден (например, ошибка в urls.py)
            return reverse('lab_list')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


# --- 2. Модели Контента Сайта (SiteSettings, MissionItem, NewsItem, Announcement, Partner) ---

class SiteSettings(models.Model):
    """Модель для общих настроек сайта (Singleton)"""
    # Hero Section Home
    hero_title_home = models.CharField(_("Заголовок Hero (Главная)"), max_length=255)
    hero_subtitle_home = models.TextField(_("Подзаголовок Hero (Главная)"))

    # About Section Text (для блока "Кто мы такие?")
    about_text_intro = RichTextField(_("Текст 'Кто мы такие?'"))
    about_image = models.ImageField(_("Фотография для блока 'Об институте'"),
                                    upload_to='site_media/',
                                    blank=True,
                                    null=True)
    # Contact Info (для футера и страницы контактов)
    address = models.CharField(_("Адрес"), max_length=255)
    phone = models.CharField(_("Телефон"), max_length=20)
    email = models.EmailField(_("Email"))

    # Contact Page Hero
    contact_hero_title = models.CharField(_("Заголовок Hero (Контакты)"), max_length=200)
    contact_hero_subtitle = models.TextField(_("Подзаголовок Hero (Контакты)"))

    class Meta:
        verbose_name = _("Общие настройки сайта")
        verbose_name_plural = _("Общие настройки сайта")

    def __str__(self):
        return "Настройки Digitalem"

    # Singleton: разрешаем только одну запись
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            return
        super().save(*args, **kwargs)


class MissionItem(TranslatableModel):
    """Модель для пунктов Миссия/Цели/Стратегия"""
    translations = TranslatedFields(
        name=models.CharField(_("Название (Миссия/Цели/Стратегия)"), max_length=100),
        description=models.TextField(_("Описание")),
    )
    icon_class = models.CharField(_("Класс иконки (e.g., bi-bullseye)"), max_length=50, blank=True)
    order = models.IntegerField(_("Порядок отображения"), default=0)

    class Meta:
        verbose_name = _("Пункт Миссия/Цели")
        verbose_name_plural = _("Миссия/Цели/Стратегия")
        ordering = ['order']

    def __str__(self):
        return self.safe_translation_getter('name', '---')


class NewsItem(TranslatableModel):
    """Модель для новостей"""
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=200),
        content=RichTextField(_("Содержание")),
        excerpt=models.TextField(_("Краткое содержание"), blank=True)
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True,
                            help_text="Автоматически генерируется из заголовка")
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


class Announcement(TranslatableModel):
    """Модель для объявлений (для боковой панели/футера)"""
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок объявления"), max_length=255),
    )
    event_date = models.DateField(_("Дата события"), default=timezone.now)

    class Meta:
        verbose_name = _("Объявление")
        verbose_name_plural = _("Объявления")
        ordering = ['event_date']

    def __str__(self):
        return self.safe_translation_getter('title', '---')


class Partner(TranslatableModel):
    """Модель для партнеров"""
    translations = TranslatedFields(
        name=models.CharField(_("Название партнера"), max_length=150),
    )
    logo = models.ImageField(_("Логотип"), upload_to='partner_logos/')
    website_url = models.URLField(_("Ссылка на сайт"), blank=True)

    def __str__(self):
        return self.safe_translation_getter('name', '---')

    class Meta:
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'


# --- 3. Вспомогательные Модели ---

class Application(models.Model):
    """Модель для Заявок/Сообщений с контактной формы"""
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
    """Модель для адресов рассылки"""
    email = models.EmailField()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class TeamMember(TranslatableModel):
    """Модель для участников команды"""
    translations = TranslatedFields(
        name=models.CharField(_('Имя и фамилия'), max_length=100),
        position=models.CharField(_('Должность'), max_length=100),
        description=models.TextField(_('Описание'))
    )
    photo = models.ImageField(_('Фотография'), upload_to='team_photos/', blank=True, null=True)
    # Социальные сети (добавлены для соответствия шаблону)
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)
    twitter_url = models.URLField(_("Twitter URL"), blank=True)

    def __str__(self):
        return self.safe_translation_getter('name', '---')

    class Meta:
        verbose_name = 'Участник команды'
        verbose_name_plural = 'Участники команды'


class SuccessFact(TranslatableModel):
    """Модель для фактов об успехе (Наши достижения)"""
    translations = TranslatedFields(
        title=models.CharField(_("Заголовок"), max_length=100),
        value=models.CharField(_("Значение"), max_length=20),
        # НОВОЕ ПОЛЕ: Подробное описание достижения
        long_description=models.TextField(_("Подробное описание"), blank=True, null=True)
    )
    # НОВОЕ ПОЛЕ: Изображение или фото
    image = models.ImageField(_("Изображение/фото"), upload_to='success_facts/', blank=True, null=True)

    icon_class = models.CharField(_("Класс иконки (e.g., bi-award-fill)"), max_length=50, default='bi-award-fill')
    order = models.IntegerField(_("Порядок отображения"), default=0)

    def __str__(self):
        return f"{self.safe_translation_getter('title', '---')}: {self.safe_translation_getter('value', '---')}"

    class Meta:
        verbose_name = 'Факт об успехе'
        verbose_name_plural = 'Факты об успехе'
        ordering = ['order']
    def __str__(self):
        return f"{self.safe_translation_getter('title', '---')}: {self.safe_translation_getter('value', '---')}"

    class Meta:
        verbose_name = 'Факт об успехе'
        verbose_name_plural = 'Факты об успехе'