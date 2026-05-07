"""cascaderelations

Revision ID: ec0fb2bde0ef
Revises: 907677b2d588
Create Date: 2026-05-07 13:22:40.867342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec0fb2bde0ef'
down_revision: Union[str, Sequence[str], None] = '907677b2d588'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('response_votes_user_id_fkey', 'response_votes', type_='foreignkey')
    op.create_foreign_key('fk_response_votes_user_id', 'response_votes', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('refresh_tokens_user_id_fkey', 'refresh_tokens', type_='foreignkey')
    op.create_foreign_key('fk_refresh_tokens_user_id', 'refresh_tokens', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('responses_user_id_fkey', 'responses', type_='foreignkey')
    op.create_foreign_key('fk_responses_user_id', 'responses', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('fk_responses_user_id', 'responses', type_='foreignkey')
    op.create_foreign_key('responses_user_id_fkey', 'responses', 'users', ['user_id'], ['id'])

    op.drop_constraint('fk_refresh_tokens_user_id', 'refresh_tokens', type_='foreignkey')
    op.create_foreign_key('refresh_tokens_user_id_fkey', 'refresh_tokens', 'users', ['user_id'], ['id'])

    op.drop_constraint('fk_response_votes_user_id', 'response_votes', type_='foreignkey')
    op.create_foreign_key('response_votes_user_id_fkey', 'response_votes', 'users', ['user_id'], ['id'])

