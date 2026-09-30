"""initial migration

Revision ID: 8ab8d5fe823d
Revises: 
Create Date: 2026-09-04 12:48:49.364246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '8ab8d5fe823d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('hotels',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=100), nullable=False),
                    sa.Column('location', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('hotels')
