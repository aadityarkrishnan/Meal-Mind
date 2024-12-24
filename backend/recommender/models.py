from mongoengine import Document, ListField, StringField, DateTimeField
from datetime import datetime


class UserRequest(Document):
    user_id = StringField(required=False)  # Optional if you're not tracking users
    ingredients = ListField(StringField(), required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    recommendations = ListField(StringField())  # Store recommended recipe names

    meta = {
        'collection': 'user_requests',
        'indexes': [
            'timestamp',
            'ingredients'
        ]
    }
