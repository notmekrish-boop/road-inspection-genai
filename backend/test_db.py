from database import get_db

db = get_db()

print("Database connected successfully!")

db.close()
