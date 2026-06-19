from app.extensions import db


class Enfermedad(db.Model):
    __tablename__ = "enfermedades"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(512), nullable=False)
    codigo_cie10 = db.Column(db.String(7))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "codigo_cie10": self.codigo_cie10,
        }
