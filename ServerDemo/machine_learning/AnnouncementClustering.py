from ServerDemo.machine_learning.Cluster import Cluster
from sklearn.metrics.pairwise import cosine_similarity

class AnnouncementClustering:
    def __init__(self, use) -> None:
        self.use = use


    def canAppendCluster(self, cluster: Cluster, announcemnt, sim_matrix):
        # check members
        for a in cluster.ids:
            if not sim_matrix[a][announcemnt.id] >= 0.9: return False

        if announcemnt.sourceId in cluster.sources: return False


        return True
    
    def check_similarity(self, s1, s2):
        pair = [s1, s2]
        vectors = self.use(pair)
        cosine_sim = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
        return cosine_sim

    def print_sim_matrix(self, sim_matrix):
        for a1, row in sim_matrix.items():
            for a2, val in sim_matrix[a1].items():
                if val >= 0.5: print(a1, a2, val)

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