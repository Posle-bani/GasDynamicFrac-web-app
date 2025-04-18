"""Remove user_id from WellState

Revision ID: 7de7eae0c7d0
Revises: 22b5ba306c04
Create Date: 2025-03-30 13:53:35.655123

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7de7eae0c7d0'
down_revision = '22b5ba306c04'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('well_states_user_id_fkey', 'well_states', type_='foreignkey')
    op.drop_column('well_states', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('well_states', sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False))
    op.create_foreign_key('well_states_user_id_fkey', 'well_states', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###
