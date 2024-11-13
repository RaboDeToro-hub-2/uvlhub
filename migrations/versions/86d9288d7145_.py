"""empty message

Revision ID: 86d9288d7145
Revises: 001
Create Date: 2024-11-13 00:01:53.833516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86d9288d7145'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('active')

    # ### end Alembic commands ###