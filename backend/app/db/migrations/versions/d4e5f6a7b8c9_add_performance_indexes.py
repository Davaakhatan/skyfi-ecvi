"""add performance indexes

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2025-01-XX 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite index for company list queries (search + date range)
    op.create_index(
        'ix_companies_legal_name_created_at',
        'companies',
        ['legal_name', 'created_at'],
        unique=False
    )
    
    # Index for registration number lookups
    op.create_index(
        'ix_companies_registration_number',
        'companies',
        ['registration_number'],
        unique=False,
        postgresql_where=sa.text('registration_number IS NOT NULL')
    )
    
    # Composite index for verification results (company + status + risk)
    op.create_index(
        'ix_verification_results_company_status_risk',
        'verification_results',
        ['company_id', 'verification_status', 'risk_score'],
        unique=False
    )
    
    # Index for latest verification per company
    op.create_index(
        'ix_verification_results_company_created',
        'verification_results',
        ['company_id', 'created_at'],
        unique=False
    )
    
    # Composite index for reviews (company + reviewer + status)
    op.create_index(
        'ix_reviews_company_reviewer_status',
        'reviews',
        ['company_id', 'reviewer_id', 'status'],
        unique=False
    )
    
    # Index for latest review per company
    op.create_index(
        'ix_reviews_company_reviewed_at',
        'reviews',
        ['company_id', 'reviewed_at'],
        unique=False
    )
    
    # Composite index for company data queries
    op.create_index(
        'ix_company_data_company_type_field',
        'company_data',
        ['company_id', 'data_type', 'field_name'],
        unique=False
    )
    
    # Index for data corrections (company + status)
    op.create_index(
        'ix_data_corrections_company_status',
        'data_corrections',
        ['company_id', 'status'],
        unique=False
    )
    
    # Index for audit logs (user + action + timestamp)
    op.create_index(
        'ix_audit_logs_user_action_created',
        'audit_logs',
        ['user_id', 'action', 'created_at'],
        unique=False
    )
    
    # Index for shared reports (token lookup)
    op.create_index(
        'ix_shared_reports_token_active',
        'shared_reports',
        ['share_token', 'is_active'],
        unique=False
    )
    
    # Index for contact verifications (company + type + status)
    op.create_index(
        'ix_contact_verifications_company_type_status',
        'contact_verification_results',
        ['company_id', 'contact_type', 'status'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_contact_verifications_company_type_status', table_name='contact_verification_results')
    op.drop_index('ix_shared_reports_token_active', table_name='shared_reports')
    op.drop_index('ix_audit_logs_user_action_created', table_name='audit_logs')
    op.drop_index('ix_data_corrections_company_status', table_name='data_corrections')
    op.drop_index('ix_company_data_company_type_field', table_name='company_data')
    op.drop_index('ix_reviews_company_reviewed_at', table_name='reviews')
    op.drop_index('ix_reviews_company_reviewer_status', table_name='reviews')
    op.drop_index('ix_verification_results_company_created', table_name='verification_results')
    op.drop_index('ix_verification_results_company_status_risk', table_name='verification_results')
    op.drop_index('ix_companies_registration_number', table_name='companies')
    op.drop_index('ix_companies_legal_name_created_at', table_name='companies')

