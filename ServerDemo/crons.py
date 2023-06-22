from django_cron import CronJobBase, Schedule
from organization.models import Organization

should_run = True

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'
    
    def do(self):
        log = open('/home/peter/VeryBigBoi/MyProjects/GP/Course-Dog-Demo/cron_log.txt', '+a')
        if not should_run:
            log.write('INFO: Job cancelled\n')
            log.close()
            return

        a = [
            {
                'id': 1,
                'content': "There's a horse outside",
                'sourceId': 1
            },
            {
                'id': 2,
                'content': "A horse is outdoors",
                'sourceId': 2
            },
            {
                'id': 3,
                'content': "I have a quiz tomorrow",
                'sourceId': 1
            },
            {
                'id': 4,
                'content': "I have a final tomorrow",
                'sourceId': 2
            },
            {
                'id': 5,
                'content': "my quiz is tomorrow",
                'sourceId': 1
            },
            {
                'id': 6,
                'content': "the section video is uploaded on gdrive",
                'sourceId': 1
            },
            {
                'id': 7,
                'content': "the section video is posted on gdrive",
                'sourceId': 2
            },
        ]
        try:
            from ServerDemo.machine_learning.MaterialClustering import UKMeansClusterer
            from ServerDemo.machine_learning.Text import TextModel
       
            x = UKMeansClusterer()
            log.write(f'INFO: started announcement clustering on {len(a)} documents\n')
            models = [
                TextModel(announcement['id'], announcement['content'], announcement['sourceId']) for announcement in a
            ]
            results = x.cluster(models)
            log.write(f'SUCCESS: {results}\n')
            log.close()

        except Exception as e:
            log.write(f'FATAL: {e}\n')
            log.close()
        