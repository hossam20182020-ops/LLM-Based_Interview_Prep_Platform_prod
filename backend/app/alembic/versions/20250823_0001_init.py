from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250823_0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'qa_sets',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('job_title', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    op.execute("""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'question_type') THEN
        CREATE TYPE question_type AS ENUM ('technical', 'behavioral');
    END IF;
END$$;
""")

    op.create_table(
        'questions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('set_id', sa.Integer, sa.ForeignKey('qa_sets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.dialects.postgresql.ENUM('technical','behavioral', name='question_type', create_type=False), nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('user_answer', sa.Text, nullable=True),
        sa.Column('difficulty', sa.Float, nullable=True),
        sa.Column('flagged', sa.Boolean, server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    op.create_index('ix_questions_set_created_at', 'questions', ['set_id', 'created_at'])
    op.create_index('ix_questions_flagged', 'questions', ['flagged'])
    op.create_check_constraint(
        'ck_questions_difficulty_range', 'questions',
        "(difficulty IS NULL) OR (difficulty >= 1 AND difficulty <= 5)"
    )

def downgrade():
    op.drop_constraint('ck_questions_difficulty_range', 'questions', type_='check')
    op.drop_index('ix_questions_flagged', table_name='questions')
    op.drop_index('ix_questions_set_created_at', table_name='questions')
    op.drop_table('questions')
    op.drop_table('qasets')
    op.execute("DROP TYPE IF EXISTS question_type")
