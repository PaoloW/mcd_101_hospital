from app.extensions import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.functions import func


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

    @hybrid_property
    def nombre_completo(self) -> str:
        """Comportamiento en Python (cuando ya tienes el objeto en memoria)"""
        partes = [self.nombres, self.primer_apellido, self.segundo_apellido]
        return " ".join(parte for parte in partes if parte)

    @nombre_completo.expression
    def nombre_completo(cls):
        """Comportamiento en SQL (cuando haces queries/filtros en la base de datos)"""
        # func.concat_ws une los textos usando un espacio ' ' eliminando nulos automáticamente
        return func.concat_ws(
            " ",
            func.nullif(cls.nombres, ""),
            func.nullif(cls.primer_apellido, ""),
            func.nullif(cls.segundo_apellido, ""),
        )


    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero_documento": self.numero_documento,
            "primer_apellido": self.primer_apellido,
            "segundo_apellido": self.segundo_apellido,
            "nombres": self.nombres,
            "fecha_nacimiento": (
                self.fecha_nacimiento.strftime("%Y-%m-%d") if self.fecha_nacimiento else None
            ),
            "sexo": self.sexo,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo,
            "nombre_completo": self.nombre_completo,
        }
