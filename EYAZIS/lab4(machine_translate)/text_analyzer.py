import nltk
from nltk import pos_tag, word_tokenize, FreqDist
from nltk.tree import Tree
import re

# Скачиваем необходимые данные NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('chunkers/maxent_ne_chunker')
except LookupError:
    nltk.download('maxent_ne_chunker')

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')


class TextAnalyzer:
    def __init__(self):
        self.pos_tag_descriptions = {
            'NOUN': 'существительное',
            'VERB': 'глагол',
            'ADJ': 'прилагательное',
            'ADV': 'наречие',
            'OTHER': 'другое'
        }

    def analyze_text(self, text):
        """Анализ текста: подсчет слов, частей речи"""
        # Токенизация
        words = word_tokenize(text)

        # Убираем пунктуацию
        words = [word for word in words if word.isalnum()]

        # Определение частей речи
        pos_tags = pos_tag(words)

        # Конвертируем теги
        converted_tags = []
        for word, tag in pos_tags:
            converted_tags.append({
                'word': word,
                'tag': self._convert_pos_tag(tag),
                'description': self.pos_tag_descriptions.get(
                    self._convert_pos_tag(tag), 'неизвестно'
                )
            })

        # Статистика по частям речи
        pos_stats = {}
        for item in converted_tags:
            tag = item['tag']
            pos_stats[tag] = pos_stats.get(tag, 0) + 1

        return {
            'word_count': len(words),
            'pos_tags': converted_tags,
            'pos_stats': pos_stats
        }

    def generate_syntax_tree(self, sentence):
        """Генерация синтаксического дерева для предложения"""
        try:
            # Токенизация и определение частей речи
            tokens = word_tokenize(sentence)
            pos_tags = pos_tag(tokens)

            # Создаем упрощенное синтаксическое дерево
            grammar = """
                S: NP VP
                NP: DT? JJ* NN
                VP: VB NP | VB ADJP
                ADJP: JJ
            """

            # Упрощенное дерево для демонстрации
            tree_structure = self._create_simple_tree(pos_tags)

            return tree_structure

        except Exception as e:
            return f"Ошибка при построении дерева: {str(e)}"

    def _create_simple_tree(self, pos_tags):
        """Создание упрощенного синтаксического дерева"""
        tree_lines = ["S"]

        for word, tag in pos_tags:
            tree_lines.append(f"  {self._convert_pos_tag(tag)}[{word}]")

        return "\n".join(tree_lines)

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