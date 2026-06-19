from app.extensions import db


class Medicamento(db.Model):
    __tablename__ = "medicamentos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(255), nullable=False)
    denominacion = db.Column(db.String(255))
    especificaciones_tecnicas = db.Column(db.Text)
    unidad_medida = db.Column(db.String(10))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "denominacion": self.denominacion,
            "especificaciones_tecnicas": self.especificaciones_tecnicas,
            "unidad_medida": self.unidad_medida,
        }
