from django_cron import CronJobBase, Schedule
from course.models import MainCourse, Course
from material.models import Material
from ServerDemo.utils import PdfReader, Logger
from ServerDemo.machine_learning.Preprocessor import Preprocessor
from ServerDemo.machine_learning.Text import TextModel
from announcement.models import Announcement
from ServerDemo.machine_learning.MaterialClustering import UKMeansClusterer
from ServerDemo.machine_learning.AnnouncementClustering import AnnouncementClustering
import tensorflow as tf
import os
import nltk

from organization.models import Organization
from course.models import Course, MainCourse
from material.models import Material

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
        nltk.download('punkt')
        self.preprocessor = Preprocessor()
        self.model = UKMeansClusterer()
        self.PROJECT_ROOT_PATH = os.getenv('PROJECT_ROOT_PATH') + '/'
    
    def get_all_materials_from_main_course(self, main_course: MainCourse, logger: Logger):
        materials = {}
        logger.info("getting all materials from courses")
        linked_courses = Course.objects.filter(main_course=main_course)
        logger.info(f"found {len(linked_courses)} subcourses")
        for linked_course in linked_courses:
            linked_course_materials = Material.objects.filter(parent_course=linked_course)
            for material in linked_course_materials:
                materials[material.id] = material
        logger.info(f"found {len(materials)} materials files")
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
            if len(cluster) <= 1: continue # skip single clusters

            original, similar = self.seperate_cluster(cluster, course_materials)

            for material in similar:
                material.similar_to = original
                material.save()


    def handle_unclustered_course(self, main_course):
        logger = Logger(f'{self.PROJECT_ROOT_PATH}/cluster_logs/material/{main_course.id}.txt')
        course_materials = self.get_all_materials_from_main_course(main_course, logger)
        material_objects = []
        for id, material in course_materials.items():
            fullpath = material.file.path
            source_id = material.parent_course
            try:
                logger.info(f"reading {fullpath}")
                content = PdfReader.read(fullpath)
                logger.info(f"preprocessing {fullpath}")
                content = self.preprocessor.preprocess_text(content)
            except Exception as e:
                logger.warn(f"failed to read or preprocess {fullpath}. Skipping...{e}")
                continue

            logger.info(f"successfully read {fullpath}")
            material_objects.append(
                TextModel(
                    id,
                    content,
                    source_id
                )
            )
        logger.info(f"starting clustering on {len(material_objects)} materials")
        try:
            results = self.model.cluster(material_objects)
        except Exception as e:
            logger.fatal(f"failed to cluster course {main_course.id} because {e}")
            logger.close()
            return False
        
        logger.info(f"finisehd clustering, saving results")
        self.handle_results(results, course_materials)
        logger.info(f"successfully clustered materials")
        logger.close()
        return True




    def do(self):
        try:
            unclustered_courses = MainCourse.objects.filter(materials_clusterd=False)
            for main_course in unclustered_courses:
                success = self.handle_unclustered_course(main_course)
                main_course.materials_clusterd = success
                main_course.save()
        except Exception as e:
            print(f'Error in material: {e}') 


class AnnouncementClusteringJob(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'ServerDemo.Announcement_Clustering'

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.PROJECT_ROOT_PATH = os.getenv('PROJECT_ROOT_PATH')
        self.nn = tf.keras.saving.load_model(f'{self.PROJECT_ROOT_PATH}/BSAM')
        self.model = AnnouncementClustering(self.nn)
    
    def get_all_announcements_from_main_course(self, main_course: MainCourse, logger):
        announcements = {}
        logger.info("getting all announcements from courses")
        linked_courses = Course.objects.filter(main_course=main_course)
        logger.info(f"found {len(linked_courses)} courses")
        for linked_course in linked_courses:
            linked_course_announcements = Announcement.objects.filter(course=linked_course)
            
            for announcement in linked_course_announcements:
                announcements[announcement.id] = announcement
        logger.info(f"found {len(announcements)} unclustered annoucement")
        return announcements
    
    def separate_cluster(self, cluster, announcements):
        most_recent = announcements[cluster[0]]
        others = []
        for id in cluster:
            if most_recent.creation_date > announcements[id].creation_date:
                most_recent = announcements[id]

        for id in cluster:
            if id == most_recent.id: continue

            others.append(announcements[id])

        return most_recent, others

    def handle_reusults(self, results, announements):
        for cluster in results:
            if len(cluster) == 1: continue

            original, similar = self.separate_cluster(cluster, announements)

            for announcement in similar:
                announcement.similar_to = original
                announcement.save()
    
    def handle_unclustered_course(self, main_course):
        logger = Logger(f'{self.PROJECT_ROOT_PATH}/cluster_logs/announcement/{main_course.id}.txt')
        course_announcements = self.get_all_announcements_from_main_course(main_course, logger)
        announcements_objects = []
        for id, announcement in course_announcements.items():
            source_id = announcement.course
            content = announcement.content
            try:
                logger.info(f"starting preprocessing on announcement {id}")
                content = self.preprocessor.preprocess_text(content, remove_numbers=False, remove_punctuation=False)
            except Exception as e:
                logger.warn(f"failed to preproccess announcement {id}. Skipping...{e}")
                continue

            announcements_objects.append(
                TextModel(
                    id,
                    content,
                    source_id
                )
            )
        logger.info(f"starting clustering on {len(announcements_objects)} announcements")
        try:
            results = self.model.cluster(announcements_objects)
        except Exception as e:
            logger.fatal(f"Failed to cluster announcements of course {main_course.id} because {e}")
            logger.close()
            return False
        self.handle_reusults(results, course_announcements)
        logger.info(f"successfully clustered announcements")
        logger.close()
        return True



    def do(self):
        try:
            unclustered_courses = MainCourse.objects.filter(announcements_clusterd=False)
            for main_course in unclustered_courses:
                success = self.handle_unclustered_course(main_course)
                main_course.announcements_clusterd = success
                main_course.save()
        except Exception as e:
            print(f"ERROR in announcement: {e}")

class DB_FILL(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'ServerDemo.DB_FILL'

    def do(self):
        try:
            org = Organization(
                faculty_name="fcai",
                organization_name="cu",
                name="fcai"
            )
            org.save()
            
            main_course = MainCourse(
                code = "CS123",
                organization=org,
                name="Mr jack"
            )
            main_course.save()

            course1 = Course(
                id="12",
                code="CS123",
                organization=org,
                name="Mr Jack 1",
                main_course = main_course
            )
            course2 = Course(
                id="21",
                code="CS123",
                organization=org,
                name="Mr Jack 2",
                main_course = main_course
            )
            course1.save(), course2.save()


            m1_1 = Material(
                id="m1",
                parent_course=course1,
                file="course_material/material1_1.pdf"
            )
            m1_2 = Material(
                id="m1_1",
                parent_course=course2,
                file="course_material/material1_2.pdf"
            )
            m2 = Material(
                id="m2",
                parent_course=course1,
                file="course_material/material2.pdf"
            )
            m1_1.save()
            m1_2.save()
            m2.save()

            a1 = Announcement(
                id=1,
                content='There\'s a squirll in your pants',
                course=course1,
            )

            a2 = Announcement(
                id=2,
                content='a squirell is in your pants',
                course=course2,
            )


            a3 = Announcement(
                id=3,
                content='tez omar kbera',
                course=course1,
            )

            a1.save()
            a2.save()
            a3.save()




        except Exception as e: 
            print(e)