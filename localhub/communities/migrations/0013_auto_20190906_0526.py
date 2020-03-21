# Generated by Django 2.2.4 on 2019-09-06 05:26

from django.db import migrations, models

import localhub.markdown.fields


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0012_auto_20190901_1129"),
    ]

    operations = [
        migrations.RemoveField(model_name="community", name="public",),
        migrations.RemoveField(model_name="historicalcommunity", name="public",),
        migrations.AddField(
            model_name="community",
            name="intro",
            field=localhub.markdown.fields.MarkdownField(
                blank=True,
                help_text="Text shown in Login and other pages to non-members.",
            ),
        ),
        migrations.AddField(
            model_name="historicalcommunity",
            name="intro",
            field=localhub.markdown.fields.MarkdownField(
                blank=True,
                help_text="Text shown in Login and other pages to non-members.",
            ),
        ),
        migrations.AlterField(
            model_name="community",
            name="description",
            field=localhub.markdown.fields.MarkdownField(
                blank=True,
                help_text="Longer description of site shown to members in Description page.",
            ),
        ),
        migrations.AlterField(
            model_name="community",
            name="tagline",
            field=models.TextField(
                blank=True, help_text="Short description shown in your Local Network."
            ),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="description",
            field=localhub.markdown.fields.MarkdownField(
                blank=True,
                help_text="Longer description of site shown to members in Description page.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="tagline",
            field=models.TextField(
                blank=True, help_text="Short description shown in your Local Network."
            ),
        ),
    ]
