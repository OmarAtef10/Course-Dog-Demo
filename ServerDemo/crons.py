from django_cron import CronJobBase, Schedule
from course.models import MainCourse, Course
from material.models import Material
from settings import PROJECT_ROOT_PATH
from PDFReader import PdfReader
from machine_learning.Preprocessor import Preprocessor
from machine_learning.Text import TextModel
from announcement.models import Announcement
from machine_learning.MaterialClustering import UKMeansClusterer

ID = 'id'
PATH = 'path'
SOURCE_ID = 'sourceId'
CREATED = 'created'
CONTENT = 'content'

class MaterialsClusteringJob(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'ServerDemo.Materials_Clustering'

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.model = UKMeansClusterer()
    
    def get_all_materials_from_main_course(self, main_course: MainCourse):
        materials = {}
        linked_courses = Course.objects.filter(main_course=main_course)
        for linked_course in linked_courses:
            linked_course_materials = Material.objects.filter(parent_course=linked_course)
            for material in linked_course_materials:
                materials[material.id] = material

        return materials
    
    def seperate_cluster(self, cluster, materials) -> Material:
        most_recent = materials[cluster[0]]
        others = []
        for id in cluster:
            if most_recent.creation_date > materials[id].creation_date:
                most_recent = materials[id]
        for id in cluster:
            if id == most_recent.id: continue
            others.append(materials[id])
        return most_recent, others
    

    def handle_results(self, results, course_materials):
        for cluster in results:
            if len(cluster) == 1: continue # skip single clusters

            original, similar = self.seperate_cluster(cluster, course_materials)

            for material in similar:
                material.similar_to = original
                material.save()


    def handle_unclustered_course(self, main_course):
        course_materials = self.get_all_materials_from_main_course(main_course)
        material_objects = []
        for _, material in course_materials.items():
            fullpath = PROJECT_ROOT_PATH + material.file_path
            id = material.id
            source_id = material.parent_course
            content = PdfReader.read(fullpath)
            content = self.preprocessor.preprocess_text(content)
            material_objects.append(
                TextModel(
                    id,
                    content,
                    source_id
                )
            )
        
        results = self.model.cluster(material_objects)
        self.handle_results(results, course_materials)





    def do(self):
        unclustered_courses = MainCourse.objects.filter(materials_clusterd=False)
        for main_course in unclustered_courses:
            self.handle_unclustered_course(main_course)
            main_course.materials_clusterd = True
            main_course.save()




class AnnouncementClusteringJob(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'ServerDemo.Announcement_Clustering'

    def __init__(self):
        self.preprocessor = Preprocessor()
    
    def get_all_announcements_from_main_course(self, main_course: MainCourse):
        announcements = {}
        linked_courses = Course.objects.filter(main_course=main_course)
        for linked_course in linked_courses:
            linked_course_announcements = Announcement.objects.filter(course=linked_course)
            
            for announcement in linked_course_announcements:
                announcements[announcement.id] = {
                    ID : announcement.id,
                    SOURCE_ID : announcement.course.id,
                    CONTENT: announcement.content,
                    CREATED: announcement.creation_date
                }
        
        return announcements
    
    def handle_unclustered_course(self, main_course):
        course_announcements = self.get_all_announcements_from_main_course(main_course)
        announcements_objects = []
        for _, announcement in course_announcements.items():
            id = announcement[ID]
            source_id = announcement[SOURCE_ID]
            content = announcement[CONTENT]
            content = self.preprocessor.preprocess_text(content, remove_numbers=False)

            announcements_objects.append(
                TextModel(
                    id,
                    content,
                    source_id
                )
            )
        # TODO: call ML model and use the results



    def do(self):
        unclustered_courses = MainCourse.objects.filter(announcements_clusterd=False)
        for main_course in unclustered_courses:
            self.handle_unclustered_course(main_course)
            main_course.announcements_clusterd = True
            main_course.save()