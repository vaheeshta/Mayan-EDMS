from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


def create_parsing_setting_for_existing_document_types(apps, schema_editor):
    DocumentType = apps.get_model('documents', 'DocumentType')
    DocumentTypeSettings = apps.get_model(
        'document_parsing', 'DocumentTypeSettings'
    )

    for document_type in DocumentType.objects.using(schema_editor.connection.alias).all():
        try:
            DocumentTypeSettings.objects.using(
                schema_editor.connection.alias
            ).create(document_type=document_type)
        except DocumentTypeSettings.DoesNotExist:
            pass


def delete_parsing_setting_for_existing_document_types(apps, schema_editor):
    DocumentType = apps.get_model('documents', 'DocumentType')
    DocumentTypeSettings = apps.get_model(
        'document_parsing', 'DocumentTypeSettings'
    )

    for document_type in DocumentType.objects.using(schema_editor.connection.alias).all():
        try:
            DocumentTypeSettings.objects.using(
                schema_editor.connection.alias
            ).get(document_type=document_type).delete()
        except DocumentTypeSettings.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0042_auto_20180403_0702'),
        ('document_parsing', '0002_auto_20170827_1617'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTypeSettings',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'auto_parsing', models.BooleanField(
                        default=True, verbose_name='Automatically queue newly '
                        'created documents for parsing.'
                    )
                ),
                (
                    'document_type', models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='parsing_settings',
                        to='documents.DocumentType',
                        verbose_name='Document type'
                    )
                ),
            ],
            options={
                'verbose_name': 'Document type settings',
                'verbose_name_plural': 'Document types settings',
            },
        ),
        migrations.RunPython(
            code=create_parsing_setting_for_existing_document_types,
            reverse_code=delete_parsing_setting_for_existing_document_types,
        )
    ]
