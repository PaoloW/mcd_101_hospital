from app.extensions import db


class CampanaSalud(db.Model):
    __tablename__ = "campanas_salud"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=True)
    objetivo = db.Column(db.Text(), nullable=True)
    desde = db.Column(db.Date, nullable=False)
    hasta = db.Column(db.Date, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "objetivo": self.objetivo,
            "desde": self.desde.isoformat() if self.desde else None,
            "hasta": self.hasta.isoformat() if self.hasta else None,
        }