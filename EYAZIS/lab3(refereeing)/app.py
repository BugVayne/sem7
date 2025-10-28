# app.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
import os
from werkzeug.utils import secure_filename
import tempfile
import io
import json
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import uuid

from file_processor import read_file
from summarizer import TextSummarizer

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Создаем временные папки
UPLOAD_FOLDER = 'uploads'
TEXT_STORAGE_FOLDER = 'text_storage'
HISTORY_FILE = 'summarization_history.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_STORAGE_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEXT_STORAGE_FOLDER'] = TEXT_STORAGE_FOLDER

# Инициализация суммаризатора
summarizer = TextSummarizer()

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_history():
    """Загружает историю реферирования из JSON файла"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
    return []


def save_history(history):
    """Сохраняет историю реферирования в JSON файл"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")


def save_text_to_file(text, text_id):
    """Сохраняет текст во временный файл"""
    try:
        file_path = os.path.join(app.config['TEXT_STORAGE_FOLDER'], f"{text_id}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return file_path
    except Exception as e:
        print(f"Error saving text: {e}")
        return None


def load_text_from_file(text_id):
    """Загружает текст из временного файла"""
    try:
        file_path = os.path.join(app.config['TEXT_STORAGE_FOLDER'], f"{text_id}.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"Error loading text: {e}")
    return None


def cleanup_old_text_files(hours=24):
    """Очищает старые временные файлы"""
    try:
        current_time = datetime.now().timestamp()
        for filename in os.listdir(app.config['TEXT_STORAGE_FOLDER']):
            if filename.endswith('.txt'):
                file_path = os.path.join(app.config['TEXT_STORAGE_FOLDER'], filename)
                file_time = os.path.getctime(file_path)
                if current_time - file_time > hours * 3600:  # 24 hours
                    os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up files: {e}")


def add_to_history(result_data):
    """Добавляет запись в историю"""
    history = load_history()

    # Ограничиваем историю последними 50 записями
    if len(history) >= 50:
        history = history[-49:]

    # Сохраняем полный текст в отдельный файл
    text_id = str(uuid.uuid4())
    save_text_to_file(result_data.get('full_text', ''), text_id)

    history.append({
        'id': len(history) + 1,
        'text_id': text_id,  # ID для загрузки полного текста
        'timestamp': datetime.now().isoformat(),
        'filename': result_data.get('filename', ''),
        'language': result_data.get('language', ''),
        'original_length': result_data.get('original_length', 0),
        'summary_length': result_data.get('summary_length', 0),
        'compression_ratio': result_data.get('compression_ratio', 0),
        'classic_summary_preview': result_data.get('classic_summary', '')[:100] + '...' if len(
            result_data.get('classic_summary', '')) > 100 else result_data.get('classic_summary', ''),
        'keyword_count': len(result_data.get('keyword_summary', [])),
        # Не сохраняем полный текст в историю JSON
        'has_full_text': True
    })

    save_history(history)
    cleanup_old_text_files()  # Очищаем старые файлы


@app.route('/')
def index():
    """Главная страница с формой загрузки"""
    return render_template('index.html')


@app.route('/help')
def help_page():
    """Страница помощи"""
    return render_template('help.html')


@app.route('/history')
def history_page():
    """Страница истории реферирования"""
    history = load_history()
    return render_template('history.html', history=history)


@app.route('/history/clear', methods=['POST'])
def clear_history():
    """Очистка истории"""
    # Также очищаем все временные текстовые файлы
    try:
        for filename in os.listdir(app.config['TEXT_STORAGE_FOLDER']):
            if filename.endswith('.txt'):
                file_path = os.path.join(app.config['TEXT_STORAGE_FOLDER'], filename)
                os.remove(file_path)
    except Exception as e:
        print(f"Error clearing text files: {e}")

    save_history([])
    flash('История очищена')
    return redirect(url_for('history_page'))


@app.route('/history/view/<int:history_id>')
def view_history_item(history_id):
    """Просмотр конкретного элемента истории"""
    history = load_history()
    item = next((item for item in history if item['id'] == history_id), None)

    if item:
        # Загружаем полный текст из файла
        full_text = load_text_from_file(item.get('text_id', ''))

        result_data = {
            'filename': item.get('filename', ''),
            'language': item.get('language', ''),
            'original_length': item.get('original_length', 0),
            'summary_length': item.get('summary_length', 0),
            'compression_ratio': item.get('compression_ratio', 0),
            'classic_summary': item.get('classic_summary_preview', ''),
            'keyword_summary': [],
            'file_size': item.get('original_length', 0),  # Приблизительно
            'original_text_preview': full_text[:500] + '...' if full_text and len(full_text) > 500 else full_text,
            'full_text': full_text,
            'upload_time': item.get('timestamp', ''),
            'text_id': item.get('text_id', '')  # Для загрузки полного текста
        }

        return render_template('result.html', result=result_data, from_history=True)
    else:
        flash('Запись не найдена')
        return redirect(url_for('history_page'))


@app.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загруженного файла"""
    if 'file' not in request.files:
        flash('Файл не выбран')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('Файл не выбран')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        try:
            # Сохраняем файл
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Обрабатываем файл
            file_info = read_file(file_path)

            # Генерируем реферат
            summary_result = summarizer.create_summary(
                file_info['text'],
                file_info['language']
            )

            # Сохраняем результаты
            summary_result['filename'] = filename
            summary_result['file_size'] = os.path.getsize(file_path)
            summary_result['original_text_preview'] = file_info['text'][:500] + '...' if len(
                file_info['text']) > 500 else file_info['text']
            summary_result['full_text'] = file_info['text']
            summary_result['upload_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            summary_result['text_id'] = str(uuid.uuid4())  # ID для загрузки полного текста

            # Сохраняем полный текст в отдельный файл
            save_text_to_file(file_info['text'], summary_result['text_id'])

            # Добавляем в историю
            add_to_history(summary_result)

            # Удаляем временный файл
            os.remove(file_path)

            return render_template('result.html', result=summary_result)

        except Exception as e:
            flash(f'Ошибка обработки файла: {str(e)}')
            return redirect(url_for('index'))

    else:
        flash('Неподдерживаемый формат файла. Разрешены только TXT файлы.')
        return redirect(url_for('index'))


@app.route('/view_full_text')
def view_full_text():
    """Просмотр полного текста исходного документа"""
    text_id = request.args.get('text_id', '')

    if text_id:
        full_text = load_text_from_file(text_id)
        if full_text:
            filename = request.args.get('filename', 'document.txt')
            return render_template('full_text.html', full_text=full_text, filename=filename)

    flash('Текст не найден')
    return redirect(url_for('index'))


@app.route('/get_full_text/<text_id>')
def get_full_text(text_id):
    """API для получения полного текста по ID"""
    full_text = load_text_from_file(text_id)
    if full_text:
        return jsonify({'success': True, 'text': full_text})
    else:
        return jsonify({'success': False, 'error': 'Text not found'})


@app.route('/download/<format_type>')
def download_summary(format_type):
    """Скачивание результатов в выбранном формате"""
    try:
        classic_summary = request.args.get('classic_summary', '')
        text_id = request.args.get('text_id', '')

        # Загружаем полный текст для PDF, если нужно
        full_text = ""
        if text_id:
            full_text = load_text_from_file(text_id)

        if format_type == 'txt':
            # Создаем временный TXT файл
            output = io.StringIO()
            output.write("АВТОМАТИЧЕСКИЙ РЕФЕРАТ ДОКУМЕНТА\n")
            output.write("=" * 50 + "\n\n")
            output.write("КЛАССИЧЕСКИЙ РЕФЕРАТ:\n")
            output.write(classic_summary + "\n\n")

            keywords = request.args.get('keywords', '[]')
            output.write("КЛЮЧЕВЫЕ СЛОВА:\n")
            output.write(", ".join(eval(keywords)) + "\n")

            mem = io.BytesIO()
            mem.write(output.getvalue().encode('utf-8'))
            mem.seek(0)

            return send_file(
                mem,
                as_attachment=True,
                download_name='summary.txt',
                mimetype='text/plain'
            )

        elif format_type == 'pdf':
            # Создаем PDF файл
            mem = io.BytesIO()
            p = canvas.Canvas(mem, pagesize=A4)

            # Простой PDF с результатами
            y_position = 800
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, y_position, "АВТОМАТИЧЕСКИЙ РЕФЕРАТ ДОКУМЕНТА")
            y_position -= 40

            p.setFont("Helvetica-Bold", 12)
            p.drawString(100, y_position, "Классический реферат:")
            y_position -= 20

            p.setFont("Helvetica", 10)
            # Добавляем текст реферата
            summary_text = classic_summary
            words = summary_text.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                if len(test_line) > 80:  # Примерная ширина строки
                    p.drawString(100, y_position, line)
                    y_position -= 15
                    line = word + " "
                    if y_position < 50:  # Новая страница
                        p.showPage()
                        y_position = 800
                        p.setFont("Helvetica", 10)
                else:
                    line = test_line

            if line:
                p.drawString(100, y_position, line)
                y_position -= 30

            p.setFont("Helvetica-Bold", 12)
            p.drawString(100, y_position, "Ключевые слова:")
            y_position -= 20

            p.setFont("Helvetica", 10)
            keywords = eval(request.args.get('keywords', '[]'))
            keyword_text = ", ".join(keywords[:10])  # Берем первые 10 ключевых слов

            # Обрабатываем ключевые слова
            words = keyword_text.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                if len(test_line) > 80:
                    p.drawString(100, y_position, line)
                    y_position -= 15
                    line = word + " "
                    if y_position < 50:
                        p.showPage()
                        y_position = 800
                        p.setFont("Helvetica", 10)
                else:
                    line = test_line

            if line:
                p.drawString(100, y_position, line)

            p.showPage()
            p.save()
            mem.seek(0)

            return send_file(
                mem,
                as_attachment=True,
                download_name='summary.pdf',
                mimetype='application/pdf'
            )

        flash('Неподдерживаемый формат для скачивания')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'Ошибка при создании файла: {str(e)}')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)