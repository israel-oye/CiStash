"""add field to Document model

Revision ID: a0b8ae7d5c78
Revises: b3135c692393
Create Date: 2023-07-06 06:00:43.955879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0b8ae7d5c78'
down_revision = 'b3135c692393'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_size', sa.String(length=10), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.drop_column('file_size')

    # ### end Alembic commands ###
