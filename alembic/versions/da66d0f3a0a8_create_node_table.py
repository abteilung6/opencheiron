"""Create node table

Revision ID: da66d0f3a0a8
Revises: 6ba95392a016
Create Date: 2023-05-27 11:15:58.801911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da66d0f3a0a8'
down_revision = '6ba95392a016'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nodes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Enum('pending', 'running', name='nodestate'), nullable=True),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nodes_id'), 'nodes', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_nodes_id'), table_name='nodes')
    op.drop_table('nodes')
    # ### end Alembic commands ###
