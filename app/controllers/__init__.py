from app.controllers.auth_controller import auth_bp
from app.controllers.persona_controller import personas_bp
from app.controllers.usuario_controller import usuarios_bp
from app.controllers.atencion_medica_controller import atenciones_bp
from app.controllers.enfermedad_controller import enfermedades_bp
from app.controllers.seccion_procedimiento_controller import secciones_procedimientos_bp
from app.controllers.procedimiento_controller import procedimientos_bp
from app.controllers.medicamento_controller import medicamentos_bp
from app.controllers.tipo_parametro_controller import tipos_parametros_bp
from app.controllers.parametro_controller import parametros_bp
from app.controllers.analisis_controller import analisis_bp
from app.controllers.diagnosticos_controller import diagnosticos_bp
from app.controllers.prescripciones_controller import prescripciones_bp
from app.controllers.procedimientos_realizados_controller import procedimientos_realizados_bp

__all__ = [
    "auth_bp",
    "personas_bp",
    "usuarios_bp",
    "atenciones_bp",
    "enfermedades_bp",
    "secciones_procedimientos_bp",
    "procedimientos_bp",
    "medicamentos_bp",
    "tipos_parametros_bp",
    "parametros_bp",
    "analisis_bp",
    "diagnosticos_bp",
    "prescripciones_bp",
    "procedimientos_realizados_bp",
]
