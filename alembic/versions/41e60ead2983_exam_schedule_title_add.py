"""exam schedule title add

Revision ID: 41e60ead2983
Revises: 273850529516
Create Date: 2024-10-10 13:28:35.438172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41e60ead2983'
down_revision: Union[str, None] = '273850529516'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('exam_schedules', sa.Column('name', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('exam_schedules', 'name')
    # ### end Alembic commands ###
