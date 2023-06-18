"""Add public ip address column

Revision ID: 6e391335e2d2
Revises: 23562dc2582d
Create Date: 2023-06-17 14:51:56.081560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e391335e2d2'
down_revision = '23562dc2582d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('nodes', sa.Column('public_ip_address', sa.String(), nullable=True))
    op.add_column('services', sa.Column('public_ip_address', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('services', 'public_ip_address')
    op.drop_column('nodes', 'public_ip_address')
    # ### end Alembic commands ###
