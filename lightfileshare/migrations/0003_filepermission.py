from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "lightfileshare",
            "0002_alter_secretfile_expire_at_alter_secretfile_password_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="FilePermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("session_id", models.CharField(blank=True, default="", max_length=64)),
                ("filename", models.CharField(max_length=255)),
                ("expires_at", models.DateTimeField()),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("session_id", "filename"),
                        name="unique_session_file_permission",
                    )
                ],
            },
        ),
    ]
