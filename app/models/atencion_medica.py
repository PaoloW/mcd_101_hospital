from app.extensions import db


class AtencionMedica(db.Model):
    __tablename__ = "atenciones_medicas"

    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    estado_atencion_id = db.Column(db.Integer, db.ForeignKey("estados_atenciones.id"), nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey("personas.id"), nullable=False)
    responsable_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    tipo_atencion_id = db.Column(db.Integer, db.ForeignKey("tipos_atenciones.id"), nullable=False)
    observacion = db.Column(db.Text(), nullable=True)

    estado_atencion = db.relationship("EstadoAtencion", backref=db.backref("atenciones_medicas", lazy=True))
    tipo_atencion = db.relationship("TipoAtencion", backref=db.backref("atenciones_medicas", lazy=True))
    paciente = db.relationship("Persona", backref=db.backref("atenciones_medicas", lazy=True))
    responsable = db.relationship("Usuario", backref=db.backref("atenciones_medicas", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fecha_hora": self.fecha_hora.isoformat(),
            "estado_atencion_id": self.estado_atencion_id,
            "paciente_id": self.paciente_id,
            "responsable_id": self.responsable_id,
            "tipo_atencion_id": self.tipo_atencion_id,
            "observacion": self.observacion,
        }
