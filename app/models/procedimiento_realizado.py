from app.extensions import db


class ProcedimientoRealizado(db.Model):
    __tablename__ = "procedimiento_realizado"

    id = db.Column(db.Integer, primary_key=True)
    procedimiento_id = db.Column(db.Integer, db.ForeignKey("procedimientos.id"), nullable=False)
    atencion_id = db.Column(db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    observacion = db.Column(db.Text(), nullable=True)
    responsable_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    atencion_medica = db.relationship(
        "AtencionMedica", backref=db.backref("procedimientos_realizados", lazy=True)
    )
    procedimiento = db.relationship("Procedimiento", backref=db.backref("procedimientos_realizados", lazy=True))
    responsable = db.relationship("Usuario", backref=db.backref("procedimientos_realizados", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "procedimiento_id": self.procedimiento_id,
            "atencion_id": self.atencion_id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "observacion": self.observacion,
            "responsable_id": self.responsable_id,
        }