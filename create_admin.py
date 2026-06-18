import sys

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    if len(sys.argv) != 3:
        print("Uso: python create_admin.py <usuario> <password>")
        sys.exit(1)

    username, password = sys.argv[1], sys.argv[2]

    if Usuario.query.filter_by(usuario=username).first():
        print(f"El usuario '{username}' ya existe.")
        sys.exit(1)

    admin = Usuario(usuario=username, rol_id=Usuario.ADMIN_ROL_ID, estado=1)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    print(f"Admin '{username}' creado correctamente.")
