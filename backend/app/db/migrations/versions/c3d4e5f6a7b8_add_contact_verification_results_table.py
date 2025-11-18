"""Add contact_verification_results table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-01-XX 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    contact_type_enum = postgresql.ENUM('EMAIL', 'PHONE', 'NAME', name='contacttype', create_type=True)
    contact_type_enum.create(op.get_bind(), checkfirst=True)
    
    contact_verification_status_enum = postgresql.ENUM('PENDING', 'VERIFIED', 'FAILED', 'PARTIAL', name='contactverificationstatus', create_type=True)
    contact_verification_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create contact_verification_results table
    op.create_table(
        'contact_verification_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('verification_result_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('contact_type', postgresql.ENUM('EMAIL', 'PHONE', 'NAME', name='contacttype'), nullable=False),
        sa.Column('contact_value', sa.String(255), nullable=False),
        sa.Column('country_code', sa.String(10), nullable=True),
        sa.Column('format_valid', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('domain_exists', sa.Boolean(), nullable=True),
        sa.Column('mx_record_exists', sa.Boolean(), nullable=True),
        sa.Column('email_exists', sa.Boolean(), nullable=True),
        sa.Column('carrier_valid', sa.Boolean(), nullable=True),
        sa.Column('carrier_name', sa.String(100), nullable=True),
        sa.Column('line_type', sa.String(50), nullable=True),
        sa.Column('name_verified', sa.Boolean(), nullable=True),
        sa.Column('public_records_match', sa.Boolean(), nullable=True),
        sa.Column('social_profiles_match', sa.Boolean(), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'VERIFIED', 'FAILED', 'PARTIAL', name='contactverificationstatus'), nullable=False, server_default='PENDING'),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('risk_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('verification_details', postgresql.JSON(), nullable=True),
        sa.Column('errors', postgresql.JSON(), nullable=True),
        sa.Column('sources_checked', postgresql.JSON(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verification_result_id'], ['verification_results.id'], ondelete='SET NULL'),
    )
    
    # Create indexes
    op.create_index('ix_contact_verification_results_id', 'contact_verification_results', ['id'])
    op.create_index('ix_contact_verification_results_company_id', 'contact_verification_results', ['company_id'])
    op.create_index('ix_contact_verification_results_verification_result_id', 'contact_verification_results', ['verification_result_id'])
    op.create_index('ix_contact_verification_results_contact_type', 'contact_verification_results', ['contact_type'])
    op.create_index('ix_contact_verification_results_status', 'contact_verification_results', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_contact_verification_results_status', table_name='contact_verification_results')
    op.drop_index('ix_contact_verification_results_contact_type', table_name='contact_verification_results')
    op.drop_index('ix_contact_verification_results_verification_result_id', table_name='contact_verification_results')
    op.drop_index('ix_contact_verification_results_company_id', table_name='contact_verification_results')
    op.drop_index('ix_contact_verification_results_id', table_name='contact_verification_results')
    
    # Drop table
    op.drop_table('contact_verification_results')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS contactverificationstatus")
    op.execute("DROP TYPE IF EXISTS contacttype")

