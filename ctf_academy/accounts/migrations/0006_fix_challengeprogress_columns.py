# Generated manually to ensure ChallengeProgress has required columns in existing DB
from django.db import migrations

SQL = [
    # Add JSON state for resume support
    "ALTER TABLE \"accounts_challengeprogress\" ADD COLUMN IF NOT EXISTS \"last_state\" jsonb NULL;",
    # Add flag for whether last save was ok
    "ALTER TABLE \"accounts_challengeprogress\" ADD COLUMN IF NOT EXISTS \"last_saved_ok\" boolean NOT NULL DEFAULT true;",
]

class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_challengeprogress_and_more"),
    ]

    operations = [
        migrations.RunSQL(sql="\n".join(SQL), reverse_sql=""),
    ]
