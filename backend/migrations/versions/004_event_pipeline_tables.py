"""Add mitigations and timeline_events tables

Revision ID: 004_event_pipeline_tables
Revises: 003d2a99a257
Create Date: 2026-08-09 14:10:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '004_event_pipeline_tables'
down_revision = '003d2a99a257'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    ALTER TYPE modelstatus ADD VALUE IF NOT EXISTS 'PRODUCTION';
    ALTER TYPE modelstatus ADD VALUE IF NOT EXISTS 'STAGING';
    ALTER TYPE modelstatus ADD VALUE IF NOT EXISTS 'VALIDATED';

    ALTER TABLE reports ADD COLUMN IF NOT EXISTS pdf_path VARCHAR(512);
    ALTER TABLE reports ADD COLUMN IF NOT EXISTS title VARCHAR(256);
    ALTER TABLE reports ADD COLUMN IF NOT EXISTS sha256_hash VARCHAR(64);

    CREATE TABLE IF NOT EXISTS mitigations (
        id UUID PRIMARY KEY,
        attack_id UUID NOT NULL REFERENCES attacks(id) ON DELETE CASCADE,
        detection_id UUID REFERENCES detections(id) ON DELETE CASCADE,
        recommended_action VARCHAR(64) NOT NULL,
        action_taken VARCHAR(64) NOT NULL,
        rule_applied TEXT,
        status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
        created_at TIMESTAMP WITH TIME ZONE NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_mitigations_attack_id ON mitigations(attack_id);
    CREATE INDEX IF NOT EXISTS ix_mitigations_detection_id ON mitigations(detection_id);

    CREATE TABLE IF NOT EXISTS timeline_events (
        id UUID PRIMARY KEY,
        attack_id UUID NOT NULL REFERENCES attacks(id) ON DELETE CASCADE,
        stage VARCHAR(64) NOT NULL,
        title VARCHAR(256) NOT NULL,
        details TEXT,
        severity VARCHAR(32) NOT NULL DEFAULT 'INFO',
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_timeline_events_attack_id ON timeline_events(attack_id);
    CREATE INDEX IF NOT EXISTS ix_timeline_events_timestamp ON timeline_events(timestamp);
    """)


def downgrade():
    op.execute("""
    DROP TABLE IF EXISTS timeline_events CASCADE;
    DROP TABLE IF EXISTS mitigations CASCADE;
    """)
