import logging
import os
from search_service import SearchService
from file_watcher import FileWatcher
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort, send_file


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


DB_CONFIG = {
    'dbname': 'search_system',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

WATCH_DIRECTORY = './documents'

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

search_service = None
file_watcher = None


@app.context_processor
def inject_globals():
    return dict(
        search_service=search_service,
        WATCH_DIRECTORY=WATCH_DIRECTORY
    )


@app.route('/')
def index():
    """Главная страница с поиском"""
    # Получаем статистику для главной страницы
    stats = {}
    if search_service:
        try:
            stats['total_docs'] = search_service.data_service.get_document_count()
            stats['avg_doc_length'] = search_service.data_service.get_avg_doc_length()
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            stats['total_docs'] = 0
            stats['avg_doc_length'] = 0
    else:
        stats['total_docs'] = 0
        stats['avg_doc_length'] = 0

    return render_template('index.html', stats=stats)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """Страница поиска"""
    if request.method == 'POST':
        query = request.form.get('query', '')
        top_k = int(request.form.get('top_k', 10))

        if not query:
            return render_template('search.html', error='Please enter a search query')

        # Use the new search method with GPT fallback
        search_response = search_service.search_with_gpt_fallback(query, top_k)

        return render_template('search.html',
                               query=query,
                               search_response=search_response,
                               results_count=len(search_response['results']))

    # GET request - показать форму
    return render_template('search.html')


@app.route('/metrics', methods=['GET', 'POST'])
def metrics():
    """Страница расчета метрик качества"""
    if request.method == 'POST':
        query = request.form.get('query', '')
        relevant_docs_text = request.form.get('relevant_docs', '')

        if not query:
            return render_template('metrics.html', error='Please enter a query')

        relevant_docs = [doc.strip() for doc in relevant_docs_text.split('\n') if doc.strip()]

        metrics_result = search_service.calculate_metrics(query, relevant_docs)
        return render_template('metrics.html',
                               metrics=metrics_result,
                               relevant_docs_text=relevant_docs_text)

    return render_template('metrics.html')


@app.route('/documents')
def documents():
    """Страница управления документами"""
    docs = search_service.data_service.get_all_documents()
    documents_info = []

    for doc_id, file_path, last_modified in docs:
        doc_details = search_service.data_service.get_document_by_path(file_path)
        if doc_details:
            documents_info.append({
                'id': doc_id,
                'title': doc_details['title'],
                'file_path': file_path,
                'date_added': doc_details['date_added'],
                'last_modified': doc_details['last_modified'],
                'doc_length': doc_details['doc_length']
            })

    return render_template('documents.html', documents=documents_info)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Страница загрузки и индексирования документов"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error='No file selected')

        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error='No file selected')

        if file and file.filename.endswith('.txt'):
            # Сохраняем файл
            file_path = os.path.join(WATCH_DIRECTORY, file.filename)
            file.save(file_path)

            # Индексируем файл
            success = search_service.index_file(file_path)

            if success:
                return render_template('upload.html',
                                       success=f'File {file.filename} successfully indexed')
            else:
                return render_template('upload.html',
                                       error=f'Failed to index file {file.filename}')

        else:
            return render_template('upload.html',
                                   error='Please upload a .txt file')

    return render_template('upload.html')


@app.route('/stats')
def stats():
    """Страница статистики"""
    total_docs = search_service.data_service.get_document_count()
    avg_doc_length = search_service.data_service.get_avg_doc_length()

    return render_template('stats.html',
                           total_docs=total_docs,
                           avg_doc_length=avg_doc_length)


@app.route('/file/<int:doc_id>')
def serve_file(doc_id):
    """Эндпоинт для отдачи файла"""
    if not search_service:
        abort(503, description="Service unavailable")

    doc = search_service.data_service.get_document_by_id(doc_id)
    if not doc:
        abort(404, description="Document not found")

    file_path = doc['file_path']

    # Проверяем существование файла
    if not os.path.exists(file_path):
        abort(404, description="File not found on disk")

    try:
        # Отдаем файл как attachment, чтобы браузер предложил скачать
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
    except Exception as e:
        logging.error(f"Error serving file {file_path}: {e}")
        abort(500, description="Error serving file")


@app.route('/preview/<int:doc_id>')
def preview_file(doc_id):
    """Эндпоинт для предпросмотра содержимого файла"""
    if not search_service:
        abort(503, description="Service unavailable")

    doc = search_service.data_service.get_document_by_id(doc_id)
    if not doc:
        abort(404, description="Document not found")

    # Возвращаем содержимое документа из базы данных
    return render_template('preview.html',
                           doc=doc,
                           content=doc['content'])

def init_directories():
    """Инициализация необходимых директорий"""
    if not os.path.exists(WATCH_DIRECTORY):
        os.makedirs(WATCH_DIRECTORY)
        logging.info(f"Создана директория: {WATCH_DIRECTORY}")

    # Создаем директорию для шаблонов
    templates_dir = './templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        logging.info(f"Создана директория: {templates_dir}")


def init_services():
    """Инициализация сервисов"""
    global search_service, file_watcher

    try:
        search_service = SearchService(DB_CONFIG)
        file_watcher = FileWatcher(WATCH_DIRECTORY, search_service)

        # Сканирование существующих файлов
        file_watcher.scan_existing_files()

        # Запуск мониторинга
        file_watcher.start()
        logging.info("Сервисы успешно инициализированы")

    except Exception as e:
        logging.error(f"Ошибка инициализации сервисов: {e}")
        raise


if __name__ == '__main__':
    # Инициализация директорий
    init_directories()

    # Инициализация сервисов
    init_services()

    try:
        # Запуск Flask приложения
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        if file_watcher:
            file_watcher.stop()
    except Exception as e:
        logging.error(f"Ошибка запуска приложения: {e}")