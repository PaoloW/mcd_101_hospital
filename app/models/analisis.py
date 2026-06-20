from app.extensions import db


class Analisis(db.Model):
    __tablename__ = "analisis"

    id = db.Column(db.Integer, primary_key=True)
    atencion_id = db.Column(
        db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=False
    )
    parametro_id = db.Column(db.Integer, db.ForeignKey("parametros.id"), nullable=False)
    valor_resultado = db.Column(db.Numeric(10, 2), nullable=True)
    observacion = db.Column(db.Text(), nullable=True)
    fechahora_muestra = db.Column(db.DateTime, nullable=False)
    fechahora_analisis = db.Column(db.DateTime, nullable=False)
    responsable_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    atencion_medica = db.relationship(
        "AtencionMedica", backref=db.backref("analisis", lazy=True)
    )
    parametro = db.relationship("Parametro", backref=db.backref("analisis", lazy=True))
    responsable = db.relationship("Usuario", backref=db.backref("analisis", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "atencion_id": self.atencion_id,
            "parametro_id": self.parametro_id,
            "valor_resultado": float(self.valor_resultado) if self.valor_resultado is not None else None,
            "observacion": self.observacion,
            "fechahora_muestra": self.fechahora_muestra.isoformat() if self.fechahora_muestra else None,
            "fechahora_analisis": self.fechahora_analisis.isoformat() if self.fechahora_analisis else None,
            "responsable_id": self.responsable_id,
        }