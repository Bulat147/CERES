"""stub for missing remote migration

Revision ID: 7cbcd43549ce
Revises: efa21a3823f0
Create Date: 2026-06-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '7cbcd43549ce'
down_revision: Union[str, Sequence[str], None] = 'efa21a3823f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
