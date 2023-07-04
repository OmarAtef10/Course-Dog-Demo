import tensorflow as tf
from .Cluster import Cluster
from .DataGenerator import DataGenerator
from .Text import TextModel
import numpy as np

class AnnouncementClustering:

    def __init__(self, model) -> None:
        self.model = model


    def canAppendCluster(self, cluster: Cluster, announcemnt, sim_matrix):
        # check members
        for a in cluster.ids:
            if not sim_matrix[a][announcemnt.id]: return False

        if announcemnt.sourceId in cluster.sources: return False


        return True
    
    def check_similarity(self, s1, s2):
        pair = np.array([[str(s1), str(s2)]])
        test = DataGenerator(
            pair, labels=None, batch_size=1, shuffle=False, include_targets=False
        )

        prob = self.model.predict(test[0], verbose=0)[0]
        label_idx = np.argmax(prob)

        return label_idx

    def init_sim_matrix(self, announcements):
        n = len(announcements)
        ids = [announcements[i].id for i in range(n)]
        sim_matrix = {
            id1: {
                id2: 0 for id2 in ids
            } for id1 in ids
        }

        for c1 in range(n):
            for c2 in range(c1+1, n):
                if announcements[c1].sourceId == announcements[c2].sourceId: continue
                announcement1, announcement2 = announcements[c1].content, announcements[c2].content
                a1_id, a2_id = announcements[c1].id, announcements[c2].id

                is_sim = self.check_similarity(announcement1, announcement2)

                sim_matrix[a1_id][a2_id] = is_sim
                sim_matrix[a2_id][a1_id] = is_sim

        return sim_matrix
    
    def extract_output(self, clusters):
        return [cluster.ids for cluster in clusters]

    def cluster(self, announcments):
        clusters = []
        sim_matrix = self.init_sim_matrix(announcments)
        clustered = [False for _ in range(len(announcments))]


        for a1 in range(len(announcments)):
            if clustered[a1]: continue
            newCluster = Cluster(
                name=announcments[a1].id,
                content=announcments[a1].content,
                sourceId=announcments[a1].sourceId
            )
            clustered[a1] = True

            for a2 in range(len(announcments)):
                if a1 == a2: continue
                if clustered[a2]: continue

                if self.canAppendCluster(newCluster, announcments[a2], sim_matrix):
                    newCluster.assign_to_cluster(announcments[a2])
                    clustered[a2] = True

            
            clusters.append(newCluster)
        
        return self.extract_output(clusters)