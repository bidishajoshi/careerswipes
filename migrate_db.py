from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        columns = [
            ("phone", "VARCHAR(20)"),
            ("location", "VARCHAR(100)"),
            ("experience_level", "VARCHAR(50)"),
            ("education", "VARCHAR(100)"),
            ("company_size", "VARCHAR(50)"),
            ("website", "VARCHAR(255)"),
            ("industry", "VARCHAR(100)"),
            ("description", "TEXT")
        ]
        
        for col, col_type in columns:
            try:
                db.session.execute(text(f"ALTER TABLE user ADD COLUMN {col} {col_type}"))
                db.session.commit()
                print(f"Added column {col}")
            except Exception as e:
                db.session.rollback()
                print(f"Skipping {col}: might already exist or error: {e}")

if __name__ == '__main__':
    migrate()
