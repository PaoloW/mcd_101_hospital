from app.extensions import db


class EstadoAtencion(db.Model):
    __tablename__ = "estados_atenciones"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
        }
