from app.extensions import db


class Participante(db.Model):
    __tablename__ = "participantes"

    id = db.Column(db.Integer, primary_key=True)
    campana_id = db.Column(db.Integer, db.ForeignKey("campanas_salud.id"), nullable=False)
    atencion_id = db.Column(db.Integer, db.ForeignKey("atenciones_medicas.id"), nullable=False)
    observacion = db.Column(db.Text(), nullable=True)

    campana = db.relationship("CampanaSalud", backref=db.backref("participantes", lazy=True))
    atencion_medica = db.relationship("AtencionMedica", backref=db.backref("participante", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "campana_id": self.campana_id,
            "atencion_id": self.atencion_id,
            "observacion": self.observacion,
        }