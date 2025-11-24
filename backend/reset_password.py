# reset_password.py

from getpass import getpass

from app.database import SessionLocal
from app.models.employee import Employee
from app.utils.security import get_password_hash


def main():
    print("=== Resetear contraseña de usuario ===")

    email = input("Email del usuario a resetear: ").strip()
    if not email:
        print("El email es obligatorio.")
        return

    new_password = getpass("Nueva contraseña: ").strip()
    if not new_password:
        print("La contraseña es obligatoria.")
        return

    db = SessionLocal()
    try:
        user = db.query(Employee).filter(Employee.email == email).first()
        if not user:
            print(f"No existe ningún usuario con el email: {email}")
            return

        user.password_hash = get_password_hash(new_password)
        db.add(user)
        db.commit()

        print(f"Contraseña actualizada correctamente para {email}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
