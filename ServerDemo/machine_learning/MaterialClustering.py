from .Cluster import Cluster
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

class UKMeansClusterer:
    def vectorize(self, cluster1: Cluster, cluster2: Cluster):
        vectorizer = TfidfVectorizer()

        v1 = vectorizer.fit_transform(cluster1.get_content())
        v2 = vectorizer.transform(cluster2.get_content())


        return [v1, v2]
    
    def calculate_similairty(self, vectors):
        centroid1 = np.mean(vectors[0].toarray(), axis = 0)
        centroid2 = np.mean(vectors[1].toarray(), axis = 0)

        return cosine_similarity(
            [centroid1],
            [centroid2]
        )[0][0]
    
    def get_cosine_similarity(self, cluster1: Cluster, cluster2: Cluster):
        try: vectors = self.vectorize(cluster1, cluster2)
        except: return 0

        return self.calculate_similairty(vectors)
    

    def should_merge(self, score): return score >= 0.8
    

    def create_sim_matrix(self, clusters: dict):
        sim_matrix = self.init_sim_matrix(clusters)

        n = len(clusters)
        for cluster1_id, cluster1 in clusters.items():
            for cluster2_id, cluster2 in clusters.items():
                if sim_matrix[cluster1_id][cluster2_id] != -1: continue
                if(cluster1_id == cluster2_id): 
                    sim_matrix[cluster1_id][cluster2_id] = 0
                    continue #dont self merge
                if(not cluster1.isdisjoint(cluster2)): 
                    sim_matrix[cluster1_id][cluster2_id] = 0
                    continue #don't merge clusters from same source

                cosine_sim = self.get_cosine_similarity(cluster1, cluster2)
                sim_matrix[cluster1_id][cluster2_id] = cosine_sim
                sim_matrix[cluster2_id][cluster1_id] = cosine_sim
            
        
        return sim_matrix
    

    def get_most_similar_cluster(self, cluster1_Id, sim_matrix):
        max_sim = 0
        max_cluster = None
        for cluster2_id, sim in sim_matrix[cluster1_Id].items():
            if sim > max_sim:
                max_sim = sim
                max_cluster = cluster2_id
        
        return max_cluster, max_sim
    

    def init_sim_matrix(self, clusters):
        return {
            cluster1.clusterId: {
                cluster2.clusterId: -1 for cluster2 in clusters.values()
            } for cluster1 in clusters.values()
        }
    
    def update_keys(self, clusters):
        return {cluster.clusterId: cluster for cluster in clusters.values()}
    def migrate_sim_matrix(self, clusters: dict, sim_matrix: dict):
        new_sim_matrix = self.init_sim_matrix(clusters)

        for _, cluster1 in clusters.items():
            for _, cluster2 in clusters.items():
                cluster1_id, cluster2_id = cluster1.clusterId, cluster2.clusterId

                if cluster1_id == cluster2_id: 
                    new_sim_matrix[cluster1_id][cluster2_id] = 0
                    continue

                if(not cluster1.isdisjoint(cluster2)): 
                    new_sim_matrix[cluster1_id][cluster2_id] = 0
                    continue #don't merge clusters from same source

                row = sim_matrix.get(cluster1_id, None)
                if row == None:
                    cosine_sim = self.get_cosine_similarity(cluster1, cluster2)
                else:   
                    cosine_sim = row.get(cluster2_id, None)
                    if cosine_sim == None:
                        cosine_sim = self.get_cosine_similarity(cluster1, cluster2)

                new_sim_matrix[cluster1_id][cluster2_id] = cosine_sim
                new_sim_matrix[cluster2_id][cluster1_id] = cosine_sim

        clusters = self.update_keys(clusters)
        return new_sim_matrix, clusters
    

    def clean_clusters(self, clusters):
        return {
            clusterId: cluster for clusterId, cluster in clusters.items() if cluster != None
        }

    def extract_output(self, clusters):
        return [cluster.ids for _, cluster in clusters.items()]


    def cluster(self, documents):
        n = len(documents)

        clusters = {
            documents[i].id: Cluster(
                documents[i].id, 
                documents[i].content, 
                documents[i].sourceId
            ) for i in range(n)
        }


        merged_cluster = True
        sim_matrix = None


        while(merged_cluster):
            merged_cluster = False

            if not sim_matrix:
                sim_matrix = self.create_sim_matrix(clusters)
            else:
                sim_matrix, clusters = self.migrate_sim_matrix(clusters, sim_matrix)

            for clusterId, cluster in clusters.items():
                most_similar_to, score = self.get_most_similar_cluster(clusterId, sim_matrix)
                
                if(self.should_merge(score) 
                    and most_similar_to != None 
                    and clusters[most_similar_to].clusterId != clusterId
                ):
                    cluster.merge_with_cluster(clusters[most_similar_to])
                    clusters[most_similar_to] = None
                    merged_cluster = True
                    break

            clusters = self.clean_clusters(clusters)

        output = self.extract_output(clusters)
        for c in output: print(c)
        return output