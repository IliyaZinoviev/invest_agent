"""init_db

Revision ID: a816d01340ea
Revises: 
Create Date: 2021-01-11 23:47:27.118450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import orm

revision = 'a816d01340ea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    stock = op.create_table('stock',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    stock_analytics = op.create_table('stock_analytics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    session.execute(stock.insert())
    session.execute(stock_analytics.insert())


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stock_analytics')
    op.drop_table('stock')
    # ### end Alembic commands ###
