"""Create blog table

Revision ID: create_blog_table
Revises: b08dfbd6ef01
Create Date: 2025-07-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_blog_table'
down_revision = 'b08dfbd6ef01'
branch_labels = None
depends_on = None


def upgrade():
    # Create blog table
    op.create_table('blog',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.String(length=20), nullable=False),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop blog table
    op.drop_table('blog')
