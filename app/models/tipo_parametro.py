from app.extensions import db


class TipoParametro(db.Model):
    __tablename__ = "tipos_parametros"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
        }
