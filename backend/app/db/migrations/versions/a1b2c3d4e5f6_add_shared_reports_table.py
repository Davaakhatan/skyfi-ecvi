"""Add shared_reports table

Revision ID: a1b2c3d4e5f6
Revises: ee425b78336f
Create Date: 2025-01-XX 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ee425b78336f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create shared_reports table
    op.create_table(
        'shared_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('verification_result_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('share_token', sa.String(64), nullable=False, unique=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verification_result_id'], ['verification_results.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    
    # Create indexes
    op.create_index('ix_shared_reports_id', 'shared_reports', ['id'])
    op.create_index('ix_shared_reports_company_id', 'shared_reports', ['company_id'])
    op.create_index('ix_shared_reports_verification_result_id', 'shared_reports', ['verification_result_id'])
    op.create_index('ix_shared_reports_share_token', 'shared_reports', ['share_token'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_shared_reports_share_token', table_name='shared_reports')
    op.drop_index('ix_shared_reports_verification_result_id', table_name='shared_reports')
    op.drop_index('ix_shared_reports_company_id', table_name='shared_reports')
    op.drop_index('ix_shared_reports_id', table_name='shared_reports')
    
    # Drop table
    op.drop_table('shared_reports')

