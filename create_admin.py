"""Crea el primer usuario admin vinculado a una persona existente.

Uso: python create_admin.py <username> <password> <numero_documento>
"""
import sys

from app import create_app
from app.extensions import db
from app.models.persona import Persona
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    if len(sys.argv) != 4:
        print("Uso: python create_admin.py <username> <password> <numero_documento>")
        sys.exit(1)

    username, password, numero_documento = sys.argv[1], sys.argv[2], sys.argv[3]

    if Usuario.query.filter_by(username=username).first():
        print(f"El usuario '{username}' ya existe.")
        sys.exit(1)

    persona = Persona.query.filter_by(numero_documento=numero_documento).first()
    if persona is None:
        print(f"No existe una persona con documento '{numero_documento}'.")
        print("Regístrela primero en Personas.")
        sys.exit(1)

    if Usuario.query.filter_by(persona_id=persona.id).first():
        print("Esa persona ya tiene un usuario asociado.")
        sys.exit(1)

    admin = Usuario(
        persona_id=persona.id,
        username=username,
        rol_id=Usuario.ADMIN_ROL_ID,
        estado=1,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    print(f"Admin '{username}' creado correctamente para {persona.nombre_completo}.")
