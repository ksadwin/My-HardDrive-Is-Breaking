"""add privacy column to User

Revision ID: 20b9a5fd9bb3
Revises: 
Create Date: 2016-09-10 15:05:31.615362

"""

# revision identifiers, used by Alembic.
revision = '20b9a5fd9bb3'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('User', sa.Column('private', sa.Boolean))


def downgrade():
    with op.batch_alter_table('User') as batch_op:
        batch_op.drop_column('private')
