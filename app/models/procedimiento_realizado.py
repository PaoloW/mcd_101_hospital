from app.extensions import db


class ProcedimientoRealizado(db.Model):
    __tablename__ = "procedimientos_realizados"

    id = db.Column(db.Integer, primary_key=True)
    atencion_medica_id = db.Column(
        db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=False
    )
    procedimiento_id = db.Column(db.Integer, db.ForeignKey("procedimientos.id"), nullable=False)
    resultado = db.Column(db.String(100), nullable=False)
    observacion = db.Column(db.Text(), nullable=True)

    atencion_medica = db.relationship(
        "AtencionMedica", backref=db.backref("procedimientos_realizados", lazy=True)
    )
    procedimiento = db.relationship("Procedimiento", backref=db.backref("procedimientos_realizados", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "atencion_medica_id": self.atencion_medica_id,
            "procedimiento_id": self.procedimiento_id,
            "resultado": self.resultado,
            "observacion": self.observacion,
        }