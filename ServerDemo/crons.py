from django_cron import CronJobBase, Schedule
from organization.models import Organization
from .globals import get_count

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'    # a unique code

    def do(self):
        new_entry = Organization(faculty_name=str(get_count()), organization_name=str(get_count()), name=str(get_count()))
        new_entry.save()