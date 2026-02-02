# Generated manually for add_villa_video

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hotel", "0019_villa_max_adults_villa_max_children_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="villa",
            name="video",
            field=models.FileField(
                blank=True,
                help_text="Upload a video for the property (e.g. MP4, WebM)",
                null=True,
                upload_to="villa_videos/",
            ),
        ),
    ]
