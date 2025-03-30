"""Add calculated report relation

Revision ID: 22b5ba306c04
Revises: 40471f012a37
Create Date: 2025-03-29 20:53:12.231858

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22b5ba306c04'
down_revision = '40471f012a37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reports', sa.Column('calculated_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'reports', 'report_calculated', ['calculated_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'reports', type_='foreignkey')
    op.drop_column('reports', 'calculated_id')
    # ### end Alembic commands ###
