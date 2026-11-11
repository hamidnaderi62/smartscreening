from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('doctor', '0002_doctorprofile_gp_org_documents'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctorprofile',
            name='specializations',
        ),
        migrations.DeleteModel(
            name='DoctorSpecialization',
        ),
    ]
