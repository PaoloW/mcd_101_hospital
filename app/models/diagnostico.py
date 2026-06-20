from app.extensions import db


class Diagnostico(db.Model):
    __tablename__ = "diagnosticos"

    id = db.Column(db.Integer, primary_key=True)
    atencion_medica_id = db.Column(
        db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=False
    )
    enfermedad_id = db.Column(db.Integer, db.ForeignKey("enfermedades.id"), nullable=False)
    observacion = db.Column(db.Text(), nullable=True)

    atencion_medica = db.relationship(
        "AtencionMedica", backref=db.backref("diagnosticos", lazy=True)
    )
    enfermedad = db.relationship("Enfermedad", backref=db.backref("diagnosticos", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "atencion_medica_id": self.atencion_medica_id,
            "enfermedad_id": self.enfermedad_id,
            "observacion": self.observacion,
        }