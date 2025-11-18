"""Add data_corrections table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-01-XX 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create correction_status enum
    correction_status_enum = postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', name='correctionstatus', create_type=True)
    correction_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create data_corrections table
    op.create_table(
        'data_corrections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_data_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('field_type', sa.String(50), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=False),
        sa.Column('correction_reason', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', name='correctionstatus'), nullable=False, server_default='PENDING'),
        sa.Column('version', sa.String(20), nullable=False, server_default='1.0'),
        sa.Column('corrected_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('previous_correction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_data_id'], ['company_data.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['corrected_by'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['previous_correction_id'], ['data_corrections.id'], ondelete='SET NULL'),
    )
    
    # Create indexes
    op.create_index('ix_data_corrections_id', 'data_corrections', ['id'])
    op.create_index('ix_data_corrections_company_id', 'data_corrections', ['company_id'])
    op.create_index('ix_data_corrections_company_data_id', 'data_corrections', ['company_data_id'])
    op.create_index('ix_data_corrections_corrected_by', 'data_corrections', ['corrected_by'])
    op.create_index('ix_data_corrections_status', 'data_corrections', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_data_corrections_status', table_name='data_corrections')
    op.drop_index('ix_data_corrections_corrected_by', table_name='data_corrections')
    op.drop_index('ix_data_corrections_company_data_id', table_name='data_corrections')
    op.drop_index('ix_data_corrections_company_id', table_name='data_corrections')
    op.drop_index('ix_data_corrections_id', table_name='data_corrections')
    
    # Drop table
    op.drop_table('data_corrections')
    
    # Drop enum
    op.execute("DROP TYPE IF EXISTS correctionstatus")

