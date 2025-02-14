"""add muballig_id column to the travellers table

Revision ID: dd4f37a1e918
Revises: 6a40f5521c39
Create Date: 2023-12-26 20:03:29.269641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd4f37a1e918'
down_revision: Union[str, None] = '6a40f5521c39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('travellers', sa.Column('muballig_id', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('travellers', 'muballig_id')
    # ### end Alembic commands ###
