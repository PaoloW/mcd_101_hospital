from app.extensions import db


class Parametro(db.Model):
    __tablename__ = "parametros"

    id = db.Column(db.Integer, primary_key=True)
    tipo_parametro_id = db.Column(
        db.Integer,
        db.ForeignKey("tipos_parametros.id"),
        nullable=False,
    )
    nombre = db.Column(db.String(255), nullable=False)
    valor_referencia_min = db.Column(db.Numeric(10, 2))
    valor_referencia_max = db.Column(db.Numeric(10, 2))
    unidad_medida = db.Column(db.String(255))
    observacion = db.Column(db.Text)

    tipo_parametro = db.relationship(
        "TipoParametro",
        backref=db.backref("parametros", lazy=True),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo_parametro_id": self.tipo_parametro_id,
            "nombre": self.nombre,
            "valor_referencia_min": (
                float(self.valor_referencia_min) if self.valor_referencia_min is not None else None
            ),
            "valor_referencia_max": (
                float(self.valor_referencia_max) if self.valor_referencia_max is not None else None
            ),
            "unidad_medida": self.unidad_medida,
            "observacion": self.observacion,
        }
