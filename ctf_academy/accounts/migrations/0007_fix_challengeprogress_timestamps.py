# Generated manually to align ChallengeProgress timestamps with model
from django.db import migrations

SQL = [
    # Ensure started_at exists and is not null
    "ALTER TABLE \"accounts_challengeprogress\" ADD COLUMN IF NOT EXISTS \"started_at\" timestamptz NOT NULL DEFAULT now();",
    # Ensure updated_at exists and is not null
    "ALTER TABLE \"accounts_challengeprogress\" ADD COLUMN IF NOT EXISTS \"updated_at\" timestamptz NOT NULL DEFAULT now();",
    # Ensure completed_at exists and is nullable
    "ALTER TABLE \"accounts_challengeprogress\" ADD COLUMN IF NOT EXISTS \"completed_at\" timestamptz NULL;",
]

class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_fix_challengeprogress_columns"),
    ]

    operations = [
        migrations.RunSQL(sql="\n".join(SQL), reverse_sql=""),
    ]
