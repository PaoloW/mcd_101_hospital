from app.extensions import db


class Analisis(db.Model):
    __tablename__ = "analisis"

    id = db.Column(db.Integer, primary_key=True)
    atencion_medica_id = db.Column(
        db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=False
    )
    parametro_id = db.Column(db.Integer, db.ForeignKey("parametros.id"), nullable=False)
    resultado = db.Column(db.String(100), nullable=False)
    observacion = db.Column(db.Text(), nullable=True)

    atencion_medica = db.relationship(
        "AtencionMedica", backref=db.backref("analisis", lazy=True)
    )
    parametro = db.relationship("Parametro", backref=db.backref("analisis", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "atencion_medica_id": self.atencion_medica_id,
            "parametro_id": self.parametro_id,
            "resultado": self.resultado,
            "observacion": self.observacion,
        }