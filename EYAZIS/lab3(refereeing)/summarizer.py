import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pymorphy3

class TextSummarizer:
    def __init__(self):
        self.russian_stopwords = set(stopwords.words('russian'))
        self.english_stopwords = set(stopwords.words('english'))
        self.english_lemmatizer = WordNetLemmatizer()
        self.russian_analyzer = pymorphy3.MorphAnalyzer()

    def preprocess_text(self, text, language):
        """
        Предобработка текста: токенизация, удаление стоп-слов, лемматизация
        """
        # Токенизация слов
        words = re.findall(r'\b\w+\b', text.lower())

        if language == 'ru':
            # Обработка для русского языка
            filtered_words = [
                word for word in words
                if word not in self.russian_stopwords and len(word) > 2
            ]
            # Лемматизация для русского
            processed_words = [
                self.russian_analyzer.parse(word)[0].normal_form
                for word in filtered_words
            ]
        else:
            # Обработка для английского языка
            filtered_words = [
                word for word in words
                if word not in self.english_stopwords and len(word) > 2
            ]
            # Лемматизация для английского
            processed_words = [
                self.english_lemmatizer.lemmatize(word)
                for word in filtered_words
            ]

        return {
            'processed_words': processed_words,
            'original_words': words
        }

    def calculate_term_weights(self, processed_text):
        """
        Вычисляет веса терминов на основе частоты встречаемости
        """
        word_freq = Counter(processed_text['processed_words'])
        total_words = len(processed_text['processed_words'])

        # Нормализация частот
        term_weights = {
            word: freq / total_words
            for word, freq in word_freq.items()
        }

        return term_weights

    def calculate_sentence_scores(self, sentences, term_weights, text_length):
        """
        Вычисляет оценку важности для каждого предложения
        """
        sentence_scores = []

        for i, sentence in enumerate(sentences):
            # Токенизация предложения
            words = re.findall(r'\b\w+\b', sentence.lower())
            score = 0
            significant_terms = 0

            for word in words:
                if word in term_weights:
                    score += term_weights[word]
                    significant_terms += 1

            # Нормализация по количеству значимых терминов
            if significant_terms > 0:
                score /= significant_terms

            # Бонус за позицию в тексте (первые предложения часто важнее)
            position_bonus = 1.0 + (0.5 * (1 - i / len(sentences)))
            score *= position_bonus

            sentence_scores.append((sentence, score))

        return sentence_scores

    def generate_classic_summary(self, sentences_with_scores, num_sentences=10):
        """
        Генерирует классический реферат из наиболее важных предложений
        """
        # Сортируем предложения по весу и берем топ-N
        sorted_sentences = sorted(
            sentences_with_scores,
            key=lambda x: x[1],
            reverse=True
        )[:num_sentences]

        # Восстанавливаем исходный порядок предложений
        original_sentences = [s[0] for s in sentences_with_scores]
        selected_indices = [
            original_sentences.index(sentence)
            for sentence, score in sorted_sentences
        ]
        selected_indices.sort()

        # Собираем итоговый текст
        summary_sentences = [
            original_sentences[i]
            for i in selected_indices
            if i < len(original_sentences)
        ]

        return ' '.join(summary_sentences)

    def generate_keyword_summary(self, term_weights, num_keywords=20):
        """
        Генерирует список ключевых слов
        """
        sorted_keywords = sorted(
            term_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )[:num_keywords]

        return [keyword for keyword, weight in sorted_keywords]

    def create_summary(self, text, language):
        """
        Основная функция генерации реферата
        """
        from file_processor import split_into_sentences

        # Разбиваем текст на предложения
        sentences = split_into_sentences(text, language)

        # Предобработка текста
        processed_text = self.preprocess_text(text, language)

        # Вычисление весов терминов
        term_weights = self.calculate_term_weights(processed_text)

        # Вычисление весов предложений
        sentence_scores = self.calculate_sentence_scores(
            sentences, term_weights, len(text)
        )

        # Генерация рефератов
        classic_summary = self.generate_classic_summary(sentence_scores)
        keyword_summary = self.generate_keyword_summary(term_weights, num_keywords=10)

        return {
            'classic_summary': classic_summary,
            'keyword_summary': keyword_summary,
            'language': language,
            'original_length': len(text),
            'summary_length': len(classic_summary),
            'compression_ratio': round((1 - len(classic_summary) / len(text)) * 100, 2)
        }