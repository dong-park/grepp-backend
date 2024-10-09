"""Initial migration

Revision ID: 273850529516
Revises: 
Create Date: 2024-10-08 23:17:27.180962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '273850529516'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exam_schedules',
    sa.Column('exam_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('max_capacity', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('end_time > start_time', name='check_end_time_after_start_time'),
    sa.CheckConstraint('max_capacity > 0', name='check_positive_max_capacity'),
    sa.PrimaryKeyConstraint('exam_id')
    )
    op.create_index(op.f('ix_exam_schedules_exam_id'), 'exam_schedules', ['exam_id'], unique=False)
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('length(hashed_password) > 8', name='check_password_length'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('reservations',
    sa.Column('reservation_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('exam_id', sa.Integer(), nullable=False),
    sa.Column('num_participants', sa.Integer(), nullable=False),
    sa.Column('is_confirmed', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('num_participants > 0', name='check_positive_participants'),
    sa.ForeignKeyConstraint(['exam_id'], ['exam_schedules.exam_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('reservation_id')
    )
    op.create_index(op.f('ix_reservations_reservation_id'), 'reservations', ['reservation_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_reservations_reservation_id'), table_name='reservations')
    op.drop_table('reservations')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_exam_schedules_exam_id'), table_name='exam_schedules')
    op.drop_table('exam_schedules')
    # ### end Alembic commands ###