from app import app, db, User  
from cryptography.fernet import Fernet
import os

encryption_key = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(encryption_key.encode()) if encryption_key else None

with app.app_context():
    users = User.query.all()
    count = 0
    for user in users:
        if user.email and not user.email.startswith('gAAAAA'):
            user.email = cipher.encrypt(user.email.encode()).decode()
            count += 1
            
    db.session.commit()
    print(f"Successfully encrypted {count} user emails!")


# raw_json = cipher.decrypt(doc.data_json.encode()).decode()
# parsed_fields = json.loads(raw_json)