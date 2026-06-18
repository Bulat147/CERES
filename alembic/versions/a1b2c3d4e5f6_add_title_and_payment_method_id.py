"""add title to locker_cells and payment_method_id to rentals/payments

Revision ID: a1b2c3d4e5f6
Revises: 7cbcd43549ce
Create Date: 2026-06-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.db.database import GUID


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7cbcd43549ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('locker_cells', sa.Column('title', sa.String(length=255), nullable=False, server_default=''))
    op.add_column('rentals', sa.Column('payment_method_id', GUID(), nullable=True))
    op.create_foreign_key('fk_rentals_payment_method_id', 'rentals', 'payment_methods', ['payment_method_id'], ['id'])
    op.add_column('payments', sa.Column('payment_method_id', GUID(), nullable=True))
    op.create_foreign_key('fk_payments_payment_method_id', 'payments', 'payment_methods', ['payment_method_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_payments_payment_method_id', 'payments', type_='foreignkey')
    op.drop_column('payments', 'payment_method_id')
    op.drop_constraint('fk_rentals_payment_method_id', 'rentals', type_='foreignkey')
    op.drop_column('rentals', 'payment_method_id')
    op.drop_column('locker_cells', 'title')
