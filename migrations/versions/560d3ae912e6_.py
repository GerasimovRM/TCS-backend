"""empty message

Revision ID: 560d3ae912e6
Revises: fb4f47341bf1
Create Date: 2022-06-09 22:37:01.387381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '560d3ae912e6'
down_revision = 'fb4f47341bf1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dbo_task', 'queue_number')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dbo_task', sa.Column('queue_number', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###