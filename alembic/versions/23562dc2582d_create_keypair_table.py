"""Create keypair table

Revision ID: 23562dc2582d
Revises: da66d0f3a0a8
Create Date: 2023-06-05 21:53:25.286450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23562dc2582d'
down_revision = 'da66d0f3a0a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('key_pairs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('key_fingerprint', sa.String(), nullable=False),
    sa.Column('key_material', sa.String(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_key_pairs_id'), 'key_pairs', ['id'], unique=False)
    op.create_index(op.f('ix_key_pairs_name'), 'key_pairs', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_key_pairs_name'), table_name='key_pairs')
    op.drop_index(op.f('ix_key_pairs_id'), table_name='key_pairs')
    op.drop_table('key_pairs')
    # ### end Alembic commands ###
