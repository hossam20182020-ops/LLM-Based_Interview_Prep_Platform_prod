# backend/app/alembic/versions/20250823_0001_init.py
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250823_0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create qa_sets table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS qa_sets (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200),
            job_title VARCHAR(200) NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
        )
    """)

    # Create enum type if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'question_type') THEN
                CREATE TYPE question_type AS ENUM ('technical', 'behavioral');
            END IF;
        END$$;
    """)

    # Create questions table if it doesn't exist
    op.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            set_id INTEGER NOT NULL REFERENCES qa_sets(id) ON DELETE CASCADE,
            type question_type NOT NULL,
            text TEXT NOT NULL,
            user_answer TEXT,
            difficulty REAL CHECK (difficulty IS NULL OR (difficulty >= 1 AND difficulty <= 5)),
            flagged BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
        )
    """)


    # Create indexes if they don't exist
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_questions_set_created_at ON questions (set_id, created_at)
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_questions_flagged ON questions (flagged)
    """)

def downgrade():
    op.drop_index('ix_questions_flagged', table_name='questions', if_exists=True)
    op.drop_index('ix_questions_set_created_at', table_name='questions', if_exists=True)
    op.drop_table('questions', if_exists=True)
    op.drop_table('qa_sets', if_exists=True)
    op.execute("DROP TYPE IF EXISTS question_type")