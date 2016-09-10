"""User drop column IP

Revision ID: 664fee54a4c4
Revises: 20b9a5fd9bb3
Create Date: 2016-09-10 16:15:59.305674

"""

# revision identifiers, used by Alembic.
revision = '664fee54a4c4'
down_revision = '20b9a5fd9bb3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('User') as batch_op:
        batch_op.drop_column('ip')


def downgrade():
    op.add_column('User', sa.Column('ip', sa.String(16)))
