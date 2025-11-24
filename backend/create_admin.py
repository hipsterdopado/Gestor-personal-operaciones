# create_admin.py

from getpass import getpass

from app.database import SessionLocal, engine, Base
from app.models.employee import Employee
from app.utils.security import get_password_hash


def main():
    print("=== Crear usuario admin ===")

    # Asegurar que las tablas existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        email = input("Email admin: ").strip()
        name = input("Nombre admin: ").strip()
        password = getpass("Password admin: ").strip()

        if not email or not name or not password:
            print("Email, nombre y password son obligatorios.")
            return

        existing = db.query(Employee).filter(Employee.email == email).first()
        if existing:
            print(f"Ya existe un usuario con ese email: {email}")
            return

        admin = Employee(
            name=name,
            email=email,
            password_hash=get_password_hash(password),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"Admin creado con id={admin.id} y email={admin.email}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
