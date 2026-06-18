from app.extensions import db


class Persona(db.Model):
    __tablename__ = "personas"

    id = db.Column(db.Integer, primary_key=True)
    numero_documento = db.Column(db.String(15), unique=True, nullable=False)
    primer_apellido = db.Column(db.String(100))
    segundo_apellido = db.Column(db.String(100))
    nombres = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(1))
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(100))
    correo = db.Column(db.String(100))

    @property
    def nombre_completo(self) -> str:
        partes = [self.nombres, self.primer_apellido, self.segundo_apellido]
        return " ".join(parte for parte in partes if parte)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero_documento": self.numero_documento,
            "primer_apellido": self.primer_apellido,
            "segundo_apellido": self.segundo_apellido,
            "nombres": self.nombres,
            "fecha_nacimiento": (
                self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None
            ),
            "sexo": self.sexo,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo,
            "nombre_completo": self.nombre_completo,
        }
