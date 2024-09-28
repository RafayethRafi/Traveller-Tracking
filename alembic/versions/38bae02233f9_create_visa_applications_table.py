"""create visa_applications table

Revision ID: 38bae02233f9
Revises: a95090aeda27
Create Date: 2024-01-04 08:01:05.722972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38bae02233f9'
down_revision: Union[str, None] = 'a95090aeda27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('visa_applications',
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('applied_muballigs', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('submission_date', sa.Date(), nullable=False),
    sa.Column('extented_date', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('file_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('visa_applications')
    # ### end Alembic commands ###
