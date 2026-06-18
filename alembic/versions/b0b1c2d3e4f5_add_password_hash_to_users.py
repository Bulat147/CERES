"""add password_hash to users

Revision ID: b0b1c2d3e4f5
Revises: a1b2c3d4e5f6
Create Date: 2026-06-18 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b0b1c2d3e4f5'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NOT NULL DEFAULT ''"
    )


def downgrade() -> None:
    op.drop_column('users', 'password_hash')
