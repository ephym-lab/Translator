"""unique_attribute_tribe

Revision ID: e91556916cb0
Revises: ec0fb2bde0ef
Create Date: 2026-05-07 13:54:43.191720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e91556916cb0'
down_revision: Union[str, Sequence[str], None] = 'ec0fb2bde0ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Remove duplicate tribe names — keep the oldest row per name, delete the rest.
    # This must run BEFORE the unique constraint is added.
    conn.execute(sa.text("""
        DELETE FROM tribes
        WHERE id NOT IN (
            SELECT DISTINCT ON (name) id
            FROM tribes
            ORDER BY name, created_at ASC
        )
    """))

    # Now it is safe to add the unique constraint.
    op.create_unique_constraint('uq_tribes_name', 'tribes', ['name'])


def downgrade() -> None:
    op.drop_constraint('uq_tribes_name', 'tribes', type_='unique')
