from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, nullable=False, default=2)
    estado = db.Column(db.Integer, nullable=False, default=1)

    ADMIN_ROL_ID = 1
    DOCTOR_ROL_ID = 2
    PACIENTE_ROL_ID = 3
    ENFERMERO_ROL_ID = 4
    LABORATORISTA_ROL_ID = 5

    def set_password(self, plain_password: str) -> None:
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        if self.password.startswith(("pbkdf2:", "scrypt:")):
            return check_password_hash(self.password, plain_password)
        return self.password == plain_password

    @property
    def is_admin(self) -> bool:
        return self.rol_id == self.ADMIN_ROL_ID

    @property
    def is_active(self) -> bool:
        return self.estado == 1

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "rol_id": self.rol_id,
            "estado": self.estado,
        }
