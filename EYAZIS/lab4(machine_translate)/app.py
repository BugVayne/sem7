from flask import Flask, render_template, request, jsonify, session
from models import db, Dictionary, TranslationHistory
from text_analyzer import TextAnalyzer
from translation_engine import TranslationEngine
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Инициализация анализатора и переводчика
analyzer = TextAnalyzer()
translator = TranslationEngine()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        domain = data.get('domain', 'computer_science')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Анализ исходного текста
        analysis_result = analyzer.analyze_text(text)

        # Перевод текста
        translation_result = translator.translate(text, domain)

        # Сохранение в историю
        if 'user_id' in session:
            history = TranslationHistory(
                user_id=session['user_id'],
                original_text=text,
                translated_text=translation_result['translated_text'],
                domain=domain,
                word_count=analysis_result['word_count']
            )
            db.session.add(history)
            db.session.commit()

        return jsonify({
            'original_text': text,
            'translated_text': translation_result['translated_text'],
            'analysis': analysis_result,
            'word_frequency': translation_result['word_frequency'],
            'translated_word_count': translation_result['translated_word_count']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze_syntax', methods=['POST'])
def analyze_syntax():
    try:
        data = request.get_json()
        sentence = data.get('sentence', '')

        if not sentence:
            return jsonify({'error': 'No sentence provided'}), 400

        syntax_tree = analyzer.generate_syntax_tree(sentence)

        return jsonify({
            'sentence': sentence,
            'syntax_tree': syntax_tree
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dictionary')
def dictionary():
    words = Dictionary.query.order_by(Dictionary.frequency.desc()).all()
    return render_template('dictionary.html', words=words)


@app.route('/dictionary/add', methods=['POST'])
def add_to_dictionary():
    try:
        data = request.get_json()
        original_word = data.get('original_word')
        translated_word = data.get('translated_word')
        pos_tag = data.get('pos_tag')

        # Проверяем, существует ли уже слово
        existing_word = Dictionary.query.filter_by(
            original_word=original_word,
            pos_tag=pos_tag
        ).first()

        if existing_word:
            existing_word.translated_word = translated_word
            existing_word.frequency += 1
        else:
            new_word = Dictionary(
                original_word=original_word,
                translated_word=translated_word,
                pos_tag=pos_tag,
                frequency=1
            )
            db.session.add(new_word)

        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dictionary/update/<int:word_id>', methods=['PUT'])
def update_dictionary(word_id):
    try:
        data = request.get_json()
        word = Dictionary.query.get_or_404(word_id)

        word.translated_word = data.get('translated_word', word.translated_word)
        word.pos_tag = data.get('pos_tag', word.pos_tag)

        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export', methods=['POST'])
def export_results():
    try:
        data = request.get_json()

        filename = f"translation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join('exports', filename)

        os.makedirs('exports', exist_ok=True)

        with open(filepath, 'w', encoding='utf-16') as f:
            f.write("МАШИННЫЙ ПЕРЕВОД - РЕЗУЛЬТАТЫ\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Исходный текст:\n{data['original_text']}\n\n")
            f.write(f"Переведенный текст:\n{data['translated_text']}\n\n")
            f.write(f"Статистика:\n")
            f.write(f"- Слов в исходном тексте: {data['analysis']['word_count']}\n")
            f.write(f"- Переведено слов: {data['translated_word_count']}\n\n")

            f.write("ЧАСТОТНЫЙ СЛОВАРЬ:\n")
            f.write("-" * 30 + "\n")
            for word_data in data['word_frequency']:
                f.write(f"{word_data['word']} -> {word_data['translation']} "
                        f"[{word_data['pos_tag']}] - {word_data['frequency']}\n")

        return jsonify({'success': True, 'filename': filename})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)