from app.extensions import db


class Prescripcion(db.Model):
    __tablename__ = "prescripciones"

    id = db.Column(db.Integer, primary_key=True)
    medicamento_id = db.Column(db.Integer, db.ForeignKey("medicamentos.id"), nullable=False)
    atencion_id = db.Column(db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=True)
    dosis = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=True)
    responsable_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)

    atencion_medica = db.relationship(
        "AtencionMedica", backref=db.backref("prescripciones", lazy=True)
    )
    medicamento = db.relationship("Medicamento", backref=db.backref("prescripciones", lazy=True))
    responsable = db.relationship("Usuario", backref=db.backref("prescripciones", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "medicamento_id": self.medicamento_id,
            "atencion_id": self.atencion_id,
            "dosis": self.dosis,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "cantidad": float(self.cantidad) if self.cantidad is not None else None,
            "responsable_id": self.responsable_id,
        }