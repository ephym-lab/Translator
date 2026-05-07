"""m2m_languages_role_admin

Revision ID: 907677b2d588
Revises: 066cc622a92f
Create Date: 2026-05-07 12:47:29.517430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '907677b2d588'
down_revision: Union[str, Sequence[str], None] = '066cc622a92f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type FIRST before using it
    role_enum = sa.Enum('admin', 'user', name='role_enum')
    role_enum.create(op.get_bind(), checkfirst=True)

    op.create_table('user_languages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('language_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['language_id'], ['languages.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'language_id', name='uq_user_language')
    )
    op.add_column('languages', sa.Column('subtribe_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'languages', 'subtribes', ['subtribe_id'], ['id'])
    op.drop_constraint(op.f('subtribes_language_id_fkey'), 'subtribes', type_='foreignkey')
    op.drop_column('subtribes', 'language_id')
    op.add_column('users', sa.Column('role', sa.Enum('admin', 'user', name='role_enum'), server_default='user', nullable=False))
    op.drop_constraint(op.f('users_language_id_fkey'), 'users', type_='foreignkey')
    op.drop_column('users', 'language_id')


def downgrade() -> None:
    op.add_column('users', sa.Column('language_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('users_language_id_fkey'), 'users', 'languages', ['language_id'], ['id'])
    op.drop_column('users', 'role')
    op.add_column('subtribes', sa.Column('language_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('subtribes_language_id_fkey'), 'subtribes', 'languages', ['language_id'], ['id'])
    op.drop_constraint(None, 'languages', type_='foreignkey')
    op.drop_column('languages', 'subtribe_id')
    op.drop_table('user_languages')

    # Drop the enum type on downgrade
    role_enum = sa.Enum('admin', 'user', name='role_enum')
    role_enum.drop(op.get_bind(), checkfirst=True)
