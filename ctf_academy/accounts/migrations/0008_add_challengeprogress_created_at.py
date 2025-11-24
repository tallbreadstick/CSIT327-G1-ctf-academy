# Manual migration to reconcile existing NOT NULL created_at column on ChallengeProgress
from django.db import migrations, models

SQL = [
    # Ensure the column exists and has a default; if it already exists we just set default to now()
    'ALTER TABLE "accounts_challengeprogress" ADD COLUMN IF NOT EXISTS "created_at" timestamptz NOT NULL DEFAULT now();',
    'ALTER TABLE "accounts_challengeprogress" ALTER COLUMN "created_at" SET DEFAULT now();',
]

class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0007_fix_challengeprogress_timestamps"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(sql='\n'.join(SQL), reverse_sql=''),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='challengeprogress',
                    name='created_at',
                    field=models.DateTimeField(auto_now_add=True),
                ),
            ],
        )
    ]
