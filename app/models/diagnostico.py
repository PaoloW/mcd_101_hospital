from app.extensions import db


class Diagnostico(db.Model):
    __tablename__ = "diagnosticos"

    id = db.Column(db.Integer, primary_key=True)
    enfermedad_id = db.Column(db.Integer, db.ForeignKey("enfermedades.id"), nullable=True)
    descripcion = db.Column(db.Text(), nullable=True)
    fecha = db.Column(db.Date, nullable=False)
    atencion_id = db.Column(db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=False)
    responsable_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    atencion_medica = db.relationship(
        "AtencionMedica", backref=db.backref("diagnosticos", lazy=True)
    )
    enfermedad = db.relationship("Enfermedad", backref=db.backref("diagnosticos", lazy=True))
    responsable = db.relationship("Usuario", backref=db.backref("diagnosticos", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "enfermedad_id": self.enfermedad_id,
            "descripcion": self.descripcion,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "atencion_id": self.atencion_id,
            "responsable_id": self.responsable_id,
        }