"""init

Revision ID: efa21a3823f0
Revises: 
Create Date: 2026-06-02 20:26:50.987843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.db.database import GUID


# revision identifiers, used by Alembic.
revision: str = 'efa21a3823f0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('locker_stations',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('address', sa.String(length=500), nullable=False),
    sa.Column('latitude', sa.DECIMAL(precision=10, scale=8), nullable=False),
    sa.Column('longitude', sa.DECIMAL(precision=11, scale=8), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.create_table('locker_cells',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('station_id', GUID(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('size', sa.String(length=20), nullable=False),
    sa.Column('hourly_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('hardware_id', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['station_id'], ['locker_stations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment_methods',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('user_id', GUID(), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('masked_pan', sa.String(length=20), nullable=False),
    sa.Column('token', sa.String(length=255), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hardware_events',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('cell_id', GUID(), nullable=False),
    sa.Column('event_type', sa.String(length=100), nullable=False),
    sa.Column('raw_payload', sa.JSON(), nullable=True),
    sa.Column('processed', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['cell_id'], ['locker_cells.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rentals',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('user_id', GUID(), nullable=False),
    sa.Column('cell_id', GUID(), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('price_per_hour', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('final_amount', sa.DECIMAL(precision=10, scale=2), nullable=True),
    sa.Column('payment_status', sa.String(length=20), nullable=False),
    sa.Column('opened_at', sa.DateTime(), nullable=True),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['cell_id'], ['locker_cells.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cell_events',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('cell_id', GUID(), nullable=False),
    sa.Column('rental_id', GUID(), nullable=True),
    sa.Column('event_type', sa.String(length=100), nullable=False),
    sa.Column('payload_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['cell_id'], ['locker_cells.id'], ),
    sa.ForeignKeyConstraint(['rental_id'], ['rentals.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', GUID(), nullable=False),
    sa.Column('rental_id', GUID(), nullable=False),
    sa.Column('user_id', GUID(), nullable=False),
    sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=True),
    sa.Column('provider_payment_id', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['rental_id'], ['rentals.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('payments')
    op.drop_table('cell_events')
    op.drop_table('rentals')
    op.drop_table('hardware_events')
    op.drop_table('payment_methods')
    op.drop_table('locker_cells')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('locker_stations')
