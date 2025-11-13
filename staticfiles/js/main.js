// Этот файл может содержать ваши пользовательские скрипты,
// например, для анимации, обработки форм или специальных виджетов.

document.addEventListener('DOMContentLoaded', function() {
    // Пример базового скрипта:
    console.log('Digitalem scripts initialized.');

    // Если вам нужно, чтобы навигационная панель меняла цвет
    // при прокрутке, код будет добавлен здесь.

    // Пример: Инициализация всех всплывающих подсказок Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});