from app.extensions import db


class SeccionProcedimiento(db.Model):
    __tablename__ = "secciones_procedimientos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    codigo = db.Column(db.String(4))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "codigo": self.codigo,
        }
