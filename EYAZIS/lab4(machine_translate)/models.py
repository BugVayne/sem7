from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_word = db.Column(db.String(100), nullable=False)
    translated_word = db.Column(db.String(100), nullable=False)
    pos_tag = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.Integer, default=1)
    domain = db.Column(db.String(50), default='general')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'original_word': self.original_word,
            'translated_word': self.translated_word,
            'pos_tag': self.pos_tag,
            'frequency': self.frequency,
            'domain': self.domain
        }


class TranslationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    translated_text = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)