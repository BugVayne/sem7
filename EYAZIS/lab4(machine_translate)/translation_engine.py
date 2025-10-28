import requests
import json
from collections import Counter
import nltk
from models import db, Dictionary


class TranslationEngine:
    def __init__(self):
        # Словари для разных предметных областей
        self.domain_dicts = {
            'computer_science': {
                'algorithm': 'Algorithmus',
                'programming': 'Programmierung',
                'software': 'Software',
                'hardware': 'Hardware',
                'database': 'Datenbank',
                'network': 'Netzwerk',
                'artificial intelligence': 'künstliche Intelligenz',
                'machine learning': 'maschinelles Lernen'
            },
            'literature': {
                'novel': 'Roman',
                'poetry': 'Poesie',
                'character': 'Charakter',
                'plot': 'Handlung',
                'theme': 'Thema',
                'metaphor': 'Metapher',
                'symbolism': 'Symbolik'
            },
            'art_criticism': {
                'painting': 'Gemälde',
                'composition': 'Komposition',
                'perspective': 'Perspektive',
                'color': 'Farbe',
                'brushwork': 'Pinselführung',
                'exhibition': 'Ausstellung',
                'masterpiece': 'Meisterwerk'
            }
        }

    def translate(self, text, domain='computer_science'):
        """Упрощенный переводчик с использованием словарей"""
        words = nltk.word_tokenize(text.lower())
        pos_tags = nltk.pos_tag(words)

        translated_words = []
        word_frequency = []
        domain_dict = self.domain_dicts[domain]

        for word, pos in pos_tags:
            # Преобразуем теги частей речи
            pos_tag = self._convert_pos_tag(pos)

            # Ищем перевод в словаре
            translation = self._lookup_translation(word, domain_dict, pos_tag)
            translated_words.append(translation)

            # Добавляем в частотный список
            word_frequency.append({
                'word': word,
                'translation': translation,
                'pos_tag': pos_tag,
                'frequency': 1
            })

        # Объединяем слова обратно в текст
        translated_text = ' '.join(translated_words)

        # Упрощенная обработка частотности
        freq_counter = Counter([item['word'] for item in word_frequency])
        for item in word_frequency:
            item['frequency'] = freq_counter[item['word']]

        # Убираем дубликаты
        unique_word_frequency = []
        seen_words = set()
        for item in word_frequency:
            if item['word'] not in seen_words:
                unique_word_frequency.append(item)
                seen_words.add(item['word'])

        # Сортируем по частоте
        unique_word_frequency.sort(key=lambda x: x['frequency'], reverse=True)

        return {
            'translated_text': translated_text,
            'word_frequency': unique_word_frequency,
            'translated_word_count': len(translated_words)
        }

    def _lookup_translation(self, word, domain_dict, pos_tag):
        """Поиск перевода слова"""
        # Сначала ищем в предметном словаре
        if word in domain_dict:
            return domain_dict[word]

        # Затем в общей базе данных
        db_word = Dictionary.query.filter_by(
            original_word=word,
            pos_tag=pos_tag
        ).first()

        if db_word:
            return db_word.translated_word

        # Если перевод не найден, возвращаем оригинальное слово
        return word

    def _convert_pos_tag(self, nltk_tag):
        """Конвертирует теги NLTK в упрощенные теги"""
        if nltk_tag.startswith('NN'):
            return 'NOUN'
        elif nltk_tag.startswith('VB'):
            return 'VERB'
        elif nltk_tag.startswith('JJ'):
            return 'ADJ'
        elif nltk_tag.startswith('RB'):
            return 'ADV'
        else:
            return 'OTHER'