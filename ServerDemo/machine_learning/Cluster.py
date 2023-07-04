class Cluster:
    def __init__(self, name, content, sourceId) -> None:
        self.members = {name: content}
        self.sourceIds = set([sourceId])
    
    def assign_to_cluster(self, member):
        self.members.update(
            {member.id: member.content}
        )
        self.sourceIds.add(member.sourceId)
    
    def merge_with_cluster(self, anotherCluster):
        self.members.update(anotherCluster.members)
        self.sourceIds.update(anotherCluster.sourceIds)

    def print(self):
        print(list(self.members.keys()))

    def get_content(self):
        return list(self.members.values())
    
    def isdisjoint(self, anotherCluster):
        return self.sourceIds.isdisjoint(anotherCluster.sourceIds)
    
    @property 
    def clusterId(self):
        return '+'.join(self.ids)

    @property
    def size(self):
        return len(self.get_content())

    @property
    def ids(self):
        return list(self.members.keys())
    
    @property
    def sources(self):
        return self.sourceIds

    @property
    def main_file_name(self):
        x = None
        for name in self.file_names:
            if len(name.split("-")) == 1:
                if x != None:
                    return None
                x = name

        return x