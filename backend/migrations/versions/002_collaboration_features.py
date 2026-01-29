"""Add collaboration features

Revision ID: 002_collaboration_features
Revises: 001_initial_migration
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_collaboration_features'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # 项目协作者表
    op.create_table('project_collaborators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), server_default='viewer'),
        sa.Column('invited_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 评论表
    op.create_table('comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comic_image_id', sa.Integer()),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('position_x', sa.Integer()),
        sa.Column('position_y', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['comic_image_id'], ['comic_images.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('comments')
    op.drop_table('project_collaborators')