"""add Timestamp to Document model

Revision ID: f534cdc1e691
Revises: 4676d8766008
Create Date: 2023-04-27 15:04:38.313929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f534cdc1e691'
down_revision = '4676d8766008'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('modified', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.drop_column('modified')
        batch_op.drop_column('created')

    # ### end Alembic commands ###