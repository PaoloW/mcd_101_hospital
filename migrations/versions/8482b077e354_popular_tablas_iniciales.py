"""popular tablas iniciales

Revision ID: 8482b077e354
Revises: 1c8b16c62277
Create Date: 2026-06-19 07:58:40.346455

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '8482b077e354'
down_revision = '1c8b16c62277'
branch_labels = None
depends_on = None

tabla_roles = table('roles',
    column('id', sa.Integer),
    column('nombre', sa.String),
)

tabla_estados_atenciones = table('estados_atenciones',
    column('id', sa.Integer),
    column('nombre', sa.String),
)

tabla_tipos_atenciones = table('tipos_atenciones',
    column('id', sa.Integer),
    column('nombre', sa.String),
)

tabla_tipos_parametros = table('tipos_parametros',
    column('id', sa.Integer),
    column('nombre', sa.String)
)

def upgrade():
    op.bulk_insert(
        tabla_roles,
        [
            {'id': 1, 'nombre': 'ADMIN'},
            {'id': 2, 'nombre': 'DOCTOR'},
            {'id': 3, 'nombre': 'PACIENTE'},
            {'id': 4, 'nombre': 'ENFERMERO'},
            {'id': 5, 'nombre': 'LABORATORISTA'},
        ]
    )
    op.bulk_insert(
        tabla_estados_atenciones,
        [
            {'id': 1, 'nombre': 'RESERVADA'},
            {'id': 2, 'nombre': 'EN PROCESO'},
            {'id': 3, 'nombre': 'FINALIZADA'},
        ]
    )
    op.bulk_insert(
        tabla_tipos_atenciones,
        [
            {'id': 1, 'nombre': 'CITA VIRTUAL'},
            {'id': 2, 'nombre': 'CITA PRESENCIAL'},
            {'id': 3, 'nombre': 'CAMPAÑA MÉDICA'},
        ]
    )
    op.bulk_insert(
        tabla_tipos_parametros,
        [
            {'id': 1, 'nombre': 'CLINICO'},
            {'id': 2, 'nombre': 'LABORATORIO'},
            {'id': 3, 'nombre': 'IMAGENOLOGÍA'},
            {'id': 4, 'nombre': 'OTROS'},
        ]
    )


def downgrade():
    op.execute("DELETE FROM roles WHERE id IN (1, 2, 3, 4, 5)")
    op.execute("DELETE FROM estados_atenciones WHERE id IN (1, 2, 3)")
    op.execute("DELETE FROM tipos_atenciones WHERE id IN (1, 2, 3)")
    op.execute("DELETE FROM tipos_parametros WHERE id IN (1, 2, 3, 4)")
