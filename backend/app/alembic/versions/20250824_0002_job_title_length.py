"""Reduce job_title length to 50 characters

Revision ID: 20250824_0002
Revises: 20250823_0001
Create Date: 2025-08-24

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250824_0002'
down_revision: Union[str, Sequence[str], None] = '20250823_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - reduce job_title length and add constraint."""
    # First, update any existing long job titles
    op.execute("""
        UPDATE qa_sets 
        SET job_title = LEFT(job_title, 50) 
        WHERE LENGTH(job_title) > 50
    """)
    
    # Then alter the column to reduce length
    op.alter_column('qa_sets', 'job_title',
                    existing_type=sa.VARCHAR(length=200),
                    type_=sa.VARCHAR(length=50),
                    existing_nullable=False)
    
    # Add check constraint for good measure
    op.create_check_constraint(
        'ck_qa_sets_job_title_length',
        'qa_sets',
        'LENGTH(job_title) <= 50 AND LENGTH(job_title) >= 1'
    )


def downgrade() -> None:
    """Downgrade schema - increase job_title length back."""
    op.drop_constraint('ck_qa_sets_job_title_length', 'qa_sets', type_='check')
    
    op.alter_column('qa_sets', 'job_title',
                    existing_type=sa.VARCHAR(length=50),
                    type_=sa.VARCHAR(length=200),
                    existing_nullable=False)