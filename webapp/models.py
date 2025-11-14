# models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from googletrans import Translator


# --- МИКСИН ДЛЯ АВТОПЕРЕВОДА ---
class AutoTranslatableModel(models.Model):
    """
    Базовый класс. Автоматически переводит поля _ru -> _en, _kk
    и генерирует slug из русского названия.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        translator = Translator()

        # Попытаемся найти поля для перевода через modeltranslation
        try:
            from modeltranslation.translator import translator as mt_translator
            trans_opts = mt_translator.get_options_for_model(self.__class__)
            fields_to_translate = trans_opts.fields.keys()
        except:
            fields_to_translate = []

        # Логика автоперевода
        for field_name in fields_to_translate:
            val_ru = getattr(self, f'{field_name}_ru', None)
            if val_ru:
                # Если нет английского - переводим
                if not getattr(self, f'{field_name}_en', None):
                    try:
                        translated = translator.translate(val_ru, src='ru', dest='en').text
                        setattr(self, f'{field_name}_en', translated)
                    except Exception:
                        pass  # Игнорируем ошибки связи с Google

                # Если нет казахского - переводим
                if not getattr(self, f'{field_name}_kk', None):
                    try:
                        translated = translator.translate(val_ru, src='ru', dest='kk').text
                        setattr(self, f'{field_name}_kk', translated)
                    except Exception:
                        pass

        # Логика генерации SLUG (из русского названия)
        # Ищем поле, похожее на название (name или title)
        if hasattr(self, 'slug') and not self.slug:
            source_text = getattr(self, 'name_ru', getattr(self, 'title_ru', None))
            # Если в _ru пусто, пробуем взять из основного поля (вдруг заполняли без суффикса)
            if not source_text:
                source_text = getattr(self, 'name', getattr(self, 'title', ''))

            if source_text:
                self.slug = slugify(source_text, allow_unicode=True)

        super().save(*args, **kwargs)


# --- 1. Основные Модели ---

class Lab(AutoTranslatableModel):
    name = models.CharField(_("Название"), max_length=100)
    description = models.TextField(_("Описание"))
    fields = models.ManyToManyField('Field', related_name='labs', blank=True)
    image = models.ImageField(upload_to='labs/', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True,
                            help_text="Автоматически из названия (ru)")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('lab_detail', kwargs={'lab_slug': self.slug})

    class Meta:
        verbose_name = 'Лаборатория'
        verbose_name_plural = 'Лаборатории'


class Field(AutoTranslatableModel):
    name = models.CharField(_("Название"), max_length=100)
    description = models.TextField(_("Описание"))
    image = models.ImageField(upload_to='fields/')
    hero_image = models.ImageField(_("Фоновое изображение Hero"), upload_to='field_heroes/', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'


class Project(AutoTranslatableModel):
    # Переводимые поля
    name = models.CharField(_("Название"), max_length=100)
    description = models.TextField(_("Краткое описание (Рекламные данные)"))
    content = RichTextField(_("Общее содержание (Полное описание)"), blank=True, null=True)
    application_area = RichTextField(_("Область применения"), blank=True, null=True)
    superiority = RichTextField(_("Превосходство по сравнению с аналогами"), blank=True, null=True)

    # Связи
    lab = models.ForeignKey('Lab', on_delete=models.SET_NULL, related_name='projects', blank=True, null=True)
    field = models.ForeignKey('Field', on_delete=models.SET_NULL, related_name='projects', blank=True, null=True)
    team = models.ManyToManyField('TeamMember', related_name='projects_involved', blank=True,
                                  verbose_name=_("Команда проекта"))
    author_member = models.ForeignKey('TeamMember', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='led_projects', verbose_name="Руководитель проекта")
    author = models.CharField(_("Автор проекта (текст)"), max_length=150, blank=True, null=True)

    # Технические поля
    slug = models.SlugField(max_length=100, unique=True, db_index=True, blank=True)
    date = models.DateField(default=timezone.now)

    # Детали
    project_url = models.URLField(_("Ссылка на проект"), blank=True, null=True)
    client_name = models.CharField(_("Заказчик / Клиент"), max_length=100, blank=True, null=True)
    year_completed = models.CharField(_("Год завершения"), max_length=4, blank=True, null=True)
    technologies = models.CharField(_("Технологии"), max_length=255, blank=True, null=True)

    # Медиа
    main_image = models.ImageField(_("Главное изображение"), upload_to='project_images/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='project_pdfs/', blank=True, null=True, verbose_name="PDF Файл")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="ID видео YouTube")

    def __str__(self):
        return self.name

    # ВЕРНУЛ СЛОЖНУЮ ЛОГИКУ URL
    def get_absolute_url(self):
        try:
            if self.lab and self.field:
                return reverse('project', kwargs={'lab_slug': self.lab.slug, 'field_slug': self.field.slug,
                                                  'project_slug': self.slug})
            elif self.lab:
                return reverse('all_projects', kwargs={'lab_slug': self.lab.slug})
            else:
                return reverse('lab_list')
        except Exception:
            return reverse('lab_list')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


# --- 2. Модели Контента Сайта ---

class SiteSettings(models.Model):
    """Модель для общих настроек сайта (Без автоперевода полей, если не нужно)"""
    hero_title_home = models.CharField(_("Заголовок Hero (Главная)"), max_length=255)
    hero_subtitle_home = models.TextField(_("Подзаголовок Hero (Главная)"))

    about_text_intro = RichTextField(_("Текст 'Кто мы такие?'"))
    about_image = models.ImageField(_("Фотография 'Об институте'"), upload_to='site_media/', blank=True, null=True)
    address = models.CharField(_("Адрес"), max_length=255)
    phone = models.CharField(_("Телефон"), max_length=20)
    email = models.EmailField(_("Email"))

    # ВЕРНУЛ ВСЕ ФОНОВЫЕ КАРТИНКИ
    hero_image_home = models.ImageField(_("Фон Hero (Главная)"), upload_to='site_backgrounds/', blank=True, null=True)
    hero_image_about = models.ImageField(_("Фон Hero (О нас)"), upload_to='site_backgrounds/', blank=True, null=True)
    hero_image_labs = models.ImageField(_("Фон Hero (Лаборатории)"), upload_to='site_backgrounds/', blank=True,
                                        null=True)
    hero_image_contacts = models.ImageField(_("Фон Hero (Контакты)"), upload_to='site_backgrounds/', blank=True,
                                            null=True)
    hero_image_news = models.ImageField(_("Фон Hero (Все новости)"), upload_to='site_backgrounds/', blank=True,
                                        null=True)

    hero_image_all_projects = models.ImageField(_("Фон Hero (Все проекты лаб.)"), upload_to='site_backgrounds/',
                                                blank=True, null=True)
    hero_image_projects_field = models.ImageField(_("Фон Hero (Проекты по направлению)"), upload_to='site_backgrounds/',
                                                  blank=True, null=True)
    hero_image_project_detail = models.ImageField(_("Фон Hero (Детальная проекта)"), upload_to='site_backgrounds/',
                                                  blank=True, null=True)
    hero_image_lab_detail = models.ImageField(_("Фон Hero (Детальная Лаборатории)"), upload_to='site_backgrounds/',
                                              blank=True, null=True)
    hero_image_news_detail = models.ImageField(_("Фон Hero (Детальная Новости)"), upload_to='site_backgrounds/',
                                               blank=True, null=True)
    hero_image_team_detail = models.ImageField(_("Фон Hero (Профиль сотрудника)"), upload_to='site_backgrounds/',
                                               blank=True, null=True)

    contact_hero_title = models.CharField(_("Заголовок Hero (Контакты)"), max_length=200)
    contact_hero_subtitle = models.TextField(_("Подзаголовок Hero (Контакты)"))

    class Meta:
        verbose_name = _("Общие настройки сайта")
        verbose_name_plural = _("Общие настройки сайта")

    def __str__(self):
        return "Настройки Digitalem"

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            return
        super().save(*args, **kwargs)


class MissionItem(AutoTranslatableModel):
    name = models.CharField(_("Название"), max_length=100)
    description = models.TextField(_("Описание"))
    icon_class = models.CharField(_("Класс иконки"), max_length=50, blank=True)
    order = models.IntegerField(_("Порядок"), default=0)

    class Meta:
        verbose_name = _("Пункт Миссия/Цели")
        verbose_name_plural = _("Миссия/Цели/Стратегия")
        ordering = ['order']

    def __str__(self):
        return self.name


class NewsItem(AutoTranslatableModel):
    title = models.CharField(_("Заголовок"), max_length=200)
    content = RichTextField(_("Содержание"))
    excerpt = models.TextField(_("Краткое содержание"), blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(_("Изображение"), upload_to='news_images/', blank=True, null=True)
    publish_date = models.DateField(_("Дата публикации"), default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'news_slug': self.slug})

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-publish_date']


class Announcement(AutoTranslatableModel):
    title = models.CharField(_("Заголовок объявления"), max_length=255)
    event_date = models.DateField(_("Дата события"), default=timezone.now)

    class Meta:
        verbose_name = _("Объявление")
        verbose_name_plural = _("Объявления")
        ordering = ['event_date']

    def __str__(self):
        return self.title


class Partner(AutoTranslatableModel):
    name = models.CharField(_("Название"), max_length=150)
    logo = models.ImageField(_("Логотип"), upload_to='partner_logos/')
    website_url = models.URLField(_("Ссылка на сайт"), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'


# --- 3. Вспомогательные Модели ---

class Management(AutoTranslatableModel):
    name = models.CharField(_('Имя и фамилия'), max_length=100)
    position = models.CharField(_('Должность'), max_length=100)
    biography = RichTextField(_('Биография'), blank=True, null=True)
    photo = models.ImageField(_('Фотография'), upload_to='management_photos/', blank=True, null=True)
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)
    order = models.IntegerField(_("Порядок"), default=0)

    orcid_id = models.CharField(_("ORCID ID"), max_length=50, blank=True, null=True)
    scopus_id = models.CharField(_("Scopus Author ID"), max_length=50, blank=True, null=True)
    publications_url = models.URLField(_("Ссылка на публикации"), blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('team_member_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Руководитель'
        verbose_name_plural = 'Руководство'
        ordering = ['order']


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


class TeamMember(AutoTranslatableModel):
    name = models.CharField(_('Имя и фамилия'), max_length=100)
    position = models.CharField(_('Должность'), max_length=100)
    description = models.TextField(_('Описание'))
    photo = models.ImageField(_('Фотография'), upload_to='team_photos/', blank=True, null=True)
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)
    twitter_url = models.URLField(_("Twitter URL"), blank=True)
    is_featured = models.BooleanField(_("Показывать в 'О нас'"), default=False)

    orcid_id = models.CharField(_("ORCID ID"), max_length=50, blank=True, null=True)
    scopus_id = models.CharField(_("Scopus Author ID"), max_length=50, blank=True, null=True)
    publications_url = models.URLField(_("Ссылка на публикации"), blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('team_member_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Участник команды'
        verbose_name_plural = 'Участники команды'


class SuccessFact(AutoTranslatableModel):
    title = models.CharField(_("Заголовок"), max_length=100)
    value = models.CharField(_("Значение"), max_length=20)
    long_description = models.TextField(_("Подробное описание"), blank=True, null=True)
    image = models.ImageField(_("Изображение"), upload_to='success_facts/', blank=True, null=True)
    icon_class = models.CharField(_("Класс иконки"), max_length=50, default='bi-award-fill')
    order = models.IntegerField(_("Порядок"), default=0)

    def __str__(self):
        return f"{self.title}: {self.value}"

    class Meta:
        verbose_name = 'Факт об успехе'
        verbose_name_plural = 'Факты об успехе'
        ordering = ['order']