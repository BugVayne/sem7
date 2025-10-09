import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from search_service import SearchService

logger = logging.getLogger(__name__)


class FileWatcher(FileSystemEventHandler):
    def __init__(self, watch_directory, search_service):
        self.watch_directory = watch_directory
        self.search_service = search_service
        self.observer = Observer()

    def start(self):
        """Запуск мониторинга"""
        self.observer.schedule(self, self.watch_directory, recursive=True)
        self.observer.start()
        logger.info(f"Мониторинг запущен для директории: {self.watch_directory}")

    def stop(self):
        """Остановка мониторинга"""
        self.observer.stop()
        self.observer.join()
        logger.info("Мониторинг остановлен")

    def on_created(self, event):
        """Обработка создания файла"""
        if not event.is_directory and event.src_path.endswith('.txt'):
            logger.info(f"Обнаружен новый файл: {event.src_path}")
            time.sleep(0.1)  # Ждем завершения записи
            self.search_service.index_file(event.src_path)

    def on_modified(self, event):
        """Обработка изменения файла"""
        if not event.is_directory and event.src_path.endswith('.txt'):
            logger.info(f"Файл изменен: {event.src_path}")
            time.sleep(0.1)
            self.search_service.index_file(event.src_path)

    def on_deleted(self, event):
        """Обработка удаления файла"""
        if not event.is_directory and event.src_path.endswith('.txt'):
            logger.info(f"Файл удален: {event.src_path}")
            self.search_service.remove_document(event.src_path)

    # В методе scan_existing_files добавьте проверку существования файлов
    def scan_existing_files(self):
        """Сканирование существующих файлов при запуске"""
        logger.info("Сканирование существующих файлов...")

        for root, dirs, files in os.walk(self.watch_directory):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    # Проверяем, существует ли файл
                    if os.path.exists(file_path):
                        self.search_service.index_file(file_path)
                    else:
                        logger.warning(f"Файл не существует: {file_path}")