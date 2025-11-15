"""Initial migration: create all tables

Revision ID: ee425b78336f
Revises: 
Create Date: 2025-11-15 10:53:18.616721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ee425b78336f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    risk_category_enum = postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', name='riskcategory', create_type=True)
    risk_category_enum.create(op.get_bind(), checkfirst=True)
    
    verification_status_enum = postgresql.ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', name='verificationstatus', create_type=True)
    verification_status_enum.create(op.get_bind(), checkfirst=True)
    
    data_type_enum = postgresql.ENUM('REGISTRATION', 'CONTACT', 'ADDRESS', name='datatype', create_type=True)
    data_type_enum.create(op.get_bind(), checkfirst=True)
    
    review_status_enum = postgresql.ENUM('PENDING', 'REVIEWED', 'FLAGGED', name='reviewstatus', create_type=True)
    review_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='operator'),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('legal_name', sa.String(255), nullable=False),
        sa.Column('registration_number', sa.String(100), nullable=True),
        sa.Column('jurisdiction', sa.String(100), nullable=True),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_companies_id', 'companies', ['id'])
    op.create_index('ix_companies_legal_name', 'companies', ['legal_name'])
    op.create_index('ix_companies_domain', 'companies', ['domain'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSON, nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_resource_id', 'audit_logs', ['resource_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    
    # Create verification_results table
    op.create_table(
        'verification_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('risk_category', risk_category_enum, nullable=False),
        sa.Column('verification_status', verification_status_enum, nullable=False, server_default='PENDING'),
        sa.Column('analysis_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analysis_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    )
    op.create_index('ix_verification_results_id', 'verification_results', ['id'])
    op.create_index('ix_verification_results_company_id', 'verification_results', ['company_id'])
    op.create_index('ix_verification_results_risk_score', 'verification_results', ['risk_score'])
    op.create_index('ix_verification_results_risk_category', 'verification_results', ['risk_category'])
    op.create_index('ix_verification_results_verification_status', 'verification_results', ['verification_status'])
    
    # Create company_data table
    op.create_table(
        'company_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data_type', data_type_enum, nullable=False),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('field_value', sa.Text, nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    )
    op.create_index('ix_company_data_id', 'company_data', ['id'])
    op.create_index('ix_company_data_company_id', 'company_data', ['company_id'])
    op.create_index('ix_company_data_data_type', 'company_data', ['data_type'])
    
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('status', review_status_enum, nullable=False, server_default='PENDING'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
    )
    op.create_index('ix_reviews_id', 'reviews', ['id'])
    op.create_index('ix_reviews_company_id', 'reviews', ['company_id'])
    op.create_index('ix_reviews_reviewer_id', 'reviews', ['reviewer_id'])
    op.create_index('ix_reviews_reviewed_at', 'reviews', ['reviewed_at'])
    op.create_index('ix_reviews_status', 'reviews', ['status'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('reviews')
    op.drop_table('company_data')
    op.drop_table('verification_results')
    op.drop_table('audit_logs')
    op.drop_table('companies')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS reviewstatus')
    op.execute('DROP TYPE IF EXISTS datatype')
    op.execute('DROP TYPE IF EXISTS verificationstatus')
    op.execute('DROP TYPE IF EXISTS riskcategory')
