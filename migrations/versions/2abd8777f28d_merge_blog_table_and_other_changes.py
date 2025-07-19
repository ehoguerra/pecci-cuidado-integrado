"""Merge blog table and other changes

Revision ID: 2abd8777f28d
Revises: 3142a2bc03c6, create_blog_table
Create Date: 2025-07-18 22:43:13.175464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2abd8777f28d'
down_revision = ('3142a2bc03c6', 'create_blog_table')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
