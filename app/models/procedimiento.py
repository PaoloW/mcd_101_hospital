from app.extensions import db


class Procedimiento(db.Model):
    __tablename__ = "procedimientos"

    id = db.Column(db.Integer, primary_key=True)
    codigo_cpms = db.Column(db.String(8), nullable=False)
    nombre = db.Column(db.String(512), nullable=False)
    seccion_procedimiento_id = db.Column(
        db.Integer,
        db.ForeignKey("secciones_procedimientos.id"),
        nullable=False,
    )

    seccion = db.relationship("SeccionProcedimiento", backref=db.backref("procedimientos", lazy=True))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo_cpms": self.codigo_cpms,
            "nombre": self.nombre,
            "seccion_procedimiento_id": self.seccion_procedimiento_id,
        }
