from app.database import Base, engine, SessionLocal
from app.models import User

def init():
    print("Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)

    print("Checking for default admin user...")
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin@example.com").first():
        admin = User(username="admin@example.com", hashed_password="admin")
        db.add(admin)
        db.commit()
        print("Admin user created: admin@example.com / admin")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == "__main__":
    init()
    