"""Add description to Camera model

Revision ID: bae66ce5e752
Revises: cf876c662946
Create Date: 2024-03-14 22:10:45.757786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bae66ce5e752'
down_revision = 'cf876c662946'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('camera', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('camera', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
