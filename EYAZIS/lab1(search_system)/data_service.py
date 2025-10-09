import psycopg2
from psycopg2.extras import DictCursor
import logging

logger = logging.getLogger(__name__)


class DataService:
    def __init__(self, db_config):
        self.db_config = db_config
        self.init_database()

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def init_database(self):
        """Инициализация таблиц БД с пересозданием всех таблиц"""
        # Сначала удаляем все таблицы в правильном порядке (из-за foreign key constraints)
        drop_queries = [
            "DROP TABLE IF EXISTS document_terms CASCADE",
            "DROP TABLE IF EXISTS terms CASCADE",
            "DROP TABLE IF EXISTS documents CASCADE"
        ]

        # Затем создаем таблицы заново
        create_queries = [
            """
            CREATE TABLE documents (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date_added DATE DEFAULT CURRENT_DATE,
                file_path TEXT UNIQUE NOT NULL,
                last_modified FLOAT,
                doc_length INTEGER
            )
            """,
            """
            CREATE TABLE terms (
                term VARCHAR(255) PRIMARY KEY,
                doc_count INTEGER DEFAULT 0
            )
            """,
            """
            CREATE TABLE document_terms (
                doc_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                term VARCHAR(255) REFERENCES terms(term) ON DELETE CASCADE,
                frequency INTEGER NOT NULL,
                PRIMARY KEY (doc_id, term)
            )
            """
        ]

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Удаляем существующие таблицы
                    logger.info("Удаление существующих таблиц...")
                    for query in drop_queries:
                        cur.execute(query)

                    # Создаем таблицы заново
                    logger.info("Создание новых таблиц...")
                    for query in create_queries:
                        cur.execute(query)

                    conn.commit()
                    logger.info("База данных успешно переинициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise

    def add_document(self, title, content, file_path, last_modified, doc_length):
        """Добавление документа в БД"""
        query = """
            INSERT INTO documents (title, content, file_path, last_modified, doc_length)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (file_path) 
            DO UPDATE SET 
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                last_modified = EXCLUDED.last_modified,
                doc_length = EXCLUDED.doc_length
            RETURNING id
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (title, content, file_path, last_modified, doc_length))
                    doc_id = cur.fetchone()[0]
                    conn.commit()
                    return doc_id
        except Exception as e:
            logger.error(f"Ошибка добавления документа: {e}")
            raise

    def delete_document(self, file_path):
        """Удаление документа по file_path и обновление статистики терминов"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Сначала получаем ID документа
                    cur.execute("SELECT id FROM documents WHERE file_path = %s", (file_path,))
                    result = cur.fetchone()
                    if not result:
                        return False

                    doc_id = result[0]

                    # Получаем все термины этого документа
                    cur.execute("SELECT term FROM document_terms WHERE doc_id = %s", (doc_id,))
                    terms = [row[0] for row in cur.fetchall()]

                    # Удаляем документ (каскадно удалит document_terms)
                    cur.execute("DELETE FROM documents WHERE file_path = %s", (file_path,))

                    # Обновляем статистику терминов
                    for term in terms:
                        # Уменьшаем doc_count на 1
                        cur.execute("""
                            UPDATE terms 
                            SET doc_count = doc_count - 1 
                            WHERE term = %s
                        """, (term,))

                        # Удаляем термины с doc_count = 0
                        cur.execute("DELETE FROM terms WHERE doc_count <= 0")

                    conn.commit()
                    return True

        except Exception as e:
            logger.error(f"Ошибка удаления документа: {e}")
            return False

    def get_document_by_path(self, file_path):
        """Получение документа по пути"""
        query = "SELECT * FROM documents WHERE file_path = %s"
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(query, (file_path,))
                    return cur.fetchone()
        except Exception as e:
            logger.error(f"Ошибка получения документа: {e}")
            return None

    def update_term_stats(self, term_frequencies):
        """Обновление статистики терминов"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Обновление счетчиков документов для терминов
                    for term in term_frequencies.keys():
                        cur.execute("""
                            INSERT INTO terms (term, doc_count) 
                            VALUES (%s, 1)
                            ON CONFLICT (term) 
                            DO UPDATE SET doc_count = terms.doc_count + 1
                        """, (term,))

                    conn.commit()
        except Exception as e:
            logger.error(f"Ошибка обновления статистики терминов: {e}")
            raise

    def add_document_terms(self, doc_id, term_frequencies):
        """Добавление терминов документа"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Удаляем старые термины документа
                    cur.execute("DELETE FROM document_terms WHERE doc_id = %s", (doc_id,))

                    # Добавляем новые термины
                    for term, freq in term_frequencies.items():
                        cur.execute("""
                            INSERT INTO document_terms (doc_id, term, frequency)
                            VALUES (%s, %s, %s)
                        """, (doc_id, term, freq))

                    conn.commit()
        except Exception as e:
            logger.error(f"Ошибка добавления терминов документа: {e}")
            raise

    def get_document_count(self):
        """Получение общего количества документов"""
        query = "SELECT COUNT(*) FROM documents"
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка получения количества документов: {e}")
            return 0

    def get_avg_doc_length(self):
        """Получение средней длины документов"""
        query = "SELECT AVG(doc_length) FROM documents WHERE doc_length IS NOT NULL"
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    result = cur.fetchone()[0]
                    return float(result) if result else 0.0
        except Exception as e:
            logger.error(f"Ошибка получения средней длины документов: {e}")
            return 0.0

    def get_term_doc_count(self, term):
        """Получение количества документов, содержащих термин"""
        query = "SELECT doc_count FROM terms WHERE term = %s"
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (term,))
                    result = cur.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            logger.error(f"Ошибка получения doc_count для термина {term}: {e}")
            return 0

    def get_document_terms(self, doc_id):
        """Получение терминов документа"""
        query = "SELECT term, frequency FROM document_terms WHERE doc_id = %s"
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (doc_id,))
                    return dict(cur.fetchall())
        except Exception as e:
            logger.error(f"Ошибка получения терминов документа {doc_id}: {e}")
            return {}

    def get_all_documents(self):
        """Получение всех документов"""
        query = "SELECT id, file_path, last_modified FROM documents"
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения документов: {e}")
            return []

    def get_document_by_id(self, doc_id):
        """Получение документа по ID"""
        query = "SELECT * FROM documents WHERE id = %s"
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(query, (doc_id,))
                    return cur.fetchone()
        except Exception as e:
            logger.error(f"Ошибка получения документа по ID {doc_id}: {e}")
            return None


if __name__ == "__main__":
    # Тестирование подключения к БД и основных операций
    db_config = {
        'dbname': 'search_system',
        'user': 'postgres',
        'password': '1234',
        'host': 'localhost',
        'port': '5432'
    }

    try:
        data_service = DataService(db_config)
        print("✅ База данных успешно инициализирована")

        # Тест добавления документа
        doc_id = data_service.add_document(
            title="Test Document",
            content="This is a test document for the search service.",
            file_path="/test/path/document1.txt",
            last_modified=1234567890.0,
            doc_length=7
        )
        print(f"✅ Документ добавлен с ID: {doc_id}")

        # Тест получения документа
        doc = data_service.get_document_by_path("/test/path/document1.txt")
        print(f"✅ Документ получен: {doc['title']}")

        # Тест обновления статистики терминов
        term_freq = {'test': 2, 'document': 1, 'search': 1}
        data_service.update_term_stats(term_freq)
        print("✅ Статистика терминов обновлена")

        # Тест добавления терминов документа
        data_service.add_document_terms(doc_id, term_freq)
        print("✅ Термины документа добавлены")

        # Проверяем статистику терминов перед удалением
        test_count = data_service.get_term_doc_count('test')
        print(f"✅ Doc count для 'test' до удаления: {test_count}")

        # Тест получения количества документов
        count = data_service.get_document_count()
        print(f"✅ Количество документов: {count}")

        # Тест получения средней длины
        avg_len = data_service.get_avg_doc_length()
        print(f"✅ Средняя длина документа: {avg_len}")

        # Тест получения терминов документа
        terms = data_service.get_document_terms(doc_id)
        print(f"✅ Термины документа: {terms}")

        # Тест удаления документа с обновлением статистики терминов
        success = data_service.delete_document("/test/path/document1.txt")
        print(f"✅ Документ удален: {success}")

        # Проверяем статистику терминов после удаления
        test_count_after = data_service.get_term_doc_count('test')
        print(f"✅ Doc count для 'test' после удаления: {test_count_after}")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")