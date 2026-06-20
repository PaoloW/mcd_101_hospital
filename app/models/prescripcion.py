from app.extensions import db


class Prescripcion(db.Model):
    __tablename__ = "prescripciones"

    id = db.Column(db.Integer, primary_key=True)
    atencion_medica_id = db.Column(
        db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=False
    )
    medicamento_id = db.Column(db.Integer, db.ForeignKey("medicamentos.id"), nullable=False)
    cantidad = db.Column(db.String(255), nullable=False)
    frecuencia = db.Column(db.String(255), nullable=False)
    via_administracion = db.Column(db.String(100), nullable=True)
    observacion = db.Column(db.Text(), nullable=True)

    atencion_medica = db.relationship(
        "AtencionMedica", backref=db.backref("prescripciones", lazy=True)
    )
    medicamento = db.relationship("Medicamento", backref=db.backref("prescripciones", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "atencion_medica_id": self.atencion_medica_id,
            "medicamento_id": self.medicamento_id,
            "cantidad": self.cantidad,
            "frecuencia": self.frecuencia,
            "via_administracion": self.via_administracion,
            "observacion": self.observacion,
        }