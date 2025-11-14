document.addEventListener('DOMContentLoaded', function() {
    console.log('Digitalem scripts initialized.');

    // Инициализация всплывающих подсказок Bootstrap (Tooltips)
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
          return new bootstrap.Tooltip(tooltipTriggerEl);
      }
      return null;
    }).filter(t => t !== null);

    // =======================================================
    // ======== ДИНАМИКА КОНТЕНТА И PDF (project.html) ========
    // =======================================================

    // ---- Универсальный переключатель для текста (Обзор, Применение, Превосходство) ----
    document.querySelectorAll('.toggle-content-button').forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.dataset.target;
            const contentContainer = document.getElementById(targetId);

            if (!contentContainer) return;

            const truncatedContent = contentContainer.querySelector('.truncated-content');
            const fullContent = contentContainer.querySelector('.full-content');

            if (contentContainer.classList.contains('expanded')) {
                // Свернуть
                if (truncatedContent) truncatedContent.classList.remove('d-none');
                if (fullContent) fullContent.classList.add('d-none');
                this.textContent = 'Развернуть';
                contentContainer.classList.remove('expanded');
            } else {
                // Развернуть
                if (truncatedContent) truncatedContent.classList.add('d-none');
                if (fullContent) fullContent.classList.remove('d-none');
                this.textContent = 'Свернуть';
                contentContainer.classList.add('expanded');
            }
        });
    });

    // ---- Переключатель для PDF-ридера ----
    const togglePdfButton = document.getElementById('toggle-pdf-reader');
    const pdfReaderContainer = document.getElementById('pdf-reader-container');

    if (togglePdfButton && pdfReaderContainer) {
        togglePdfButton.addEventListener('click', function () {
            const isHidden = pdfReaderContainer.classList.contains('d-none');

            if (isHidden) {
                // Показать
                pdfReaderContainer.classList.remove('d-none');
                this.innerHTML = 'Скрыть PDF документ';
            } else {
                // Скрыть
                pdfReaderContainer.classList.add('d-none');
                this.innerHTML = 'Просмотр PDF документа';
            }
        });
    }

    // ---- Плеер YouTube (Очистка ссылок) ----
    document.querySelectorAll('iframe[src*="youtube.com/embed"]').forEach(iframe => {
        let src = iframe.src;
        if (src.includes('cut')) {
            console.warn('YouTube URL may need manual formatting (input only the video ID in the admin panel).');
        }
    });
});