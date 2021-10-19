# Generated by Django 3.2.8 on 2021-10-19 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExtractedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='extracted_images/')),
            ],
        ),
        migrations.CreateModel(
            name='PDF_Caption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, default='', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PDF_Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PDF_File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf', models.FileField(upload_to='pdf_repository/')),
                ('image', models.ManyToManyField(blank=True, to='pdfs.ExtractedImage')),
            ],
        ),
        migrations.AddField(
            model_name='extractedimage',
            name='caption',
            field=models.ManyToManyField(blank=True, to='pdfs.PDF_Caption'),
        ),
    ]
