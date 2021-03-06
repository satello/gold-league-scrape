"""Tables

Revision ID: 9018e062992b
Revises: None
Create Date: 2017-06-13 11:53:27.333242

"""

# revision identifiers, used by Alembic.
revision = '9018e062992b'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('owners',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('cap_room', sa.Integer(), nullable=True),
    sa.Column('years_remaining', sa.Integer(), nullable=True),
    sa.Column('spots_available', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('players',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('position', sa.Enum('QB', 'RB', 'WR', 'TE', 'PICK', name='positions'), nullable=False),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('cost', sa.Integer(), nullable=True),
    sa.Column('years', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['owners.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('players')
    op.drop_table('owners')
    ### end Alembic commands ###
