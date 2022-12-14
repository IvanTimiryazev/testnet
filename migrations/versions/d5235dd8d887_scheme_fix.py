"""scheme fix

Revision ID: d5235dd8d887
Revises: cc5d52a50060
Create Date: 2022-12-26 02:26:50.135598

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd5235dd8d887'
down_revision = 'cc5d52a50060'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_username', table_name='users')
    op.drop_column('users', 'username')
    op.drop_column('users', 'phone_number')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('phone_number', mysql.VARCHAR(length=50), nullable=True))
    op.add_column('users', sa.Column('username', mysql.VARCHAR(length=100), nullable=True))
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    # ### end Alembic commands ###
