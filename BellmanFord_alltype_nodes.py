#Author: Greg Murray (adapted from code by Neelam Yadav https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/)
#Description: Bellman-Ford Shortest Distance algorithm for string node names

import pandas as pd

class Graph:
    def __init__(self):
        self.graph = []
        self.nodes = []
        self.top_recs = []
    
    def addEdge(self, u,vw):
        self.graph.append((u,vw[0], vw[1]))
    
    def createFromCsv(self, fpath, delim=",", head=None):
        df=pd.read_csv(fpath, sep=delim,header=head)
        self.graph = df.values
        
    def setVertices(self):
        for e in self.graph:
            if e[0] not in self.nodes:
                self.nodes.append(e[0])
            if e[1] not in self.nodes:
                self.nodes.append(e[1])
        
    def printArr(self, dist):
        print("Vertex   Distance from Source")
        for k in dist:
            if dist[k]==float("Inf"):
                print(k, "inf")
            else:    
                print(k, dist[k])
                
    def topRecommendations(self, dist, n):
        self.top_recs = sorted(dist, key=dist.get)
        if n> len(dist):
            return self.top_recs
        return self.top_recs[1:n+1]
    
    def BellmanFord(self, src):
        print(self.graph)
        #initialize vertices array
        self.setVertices()
        
        #create dictionary dist
        dist = {}
        for n in self.nodes:
            dist[n] = float("Inf")
        dist[src] = 0
        print('nodes:', self.nodes)
        
        for i in range(len(self.nodes)-1):
            for u, v, w in self.graph:
                if abs(dist[u]+w) < abs(dist[v]):
                    dist[v]=dist[u]+w
        for k in dist:
            dist[k] = abs(dist[k])
        self.printArr(dist)
        print(self.topRecommendations(dist, 3))

# g = Graph()
# g.addEdge('d', 'c', 5)
# g.addEdge('a', 'b', -1)
# g.addEdge('a', 'c', 4)
# g.addEdge('b', 'c', 3)
# g.addEdge('b', 'd', 2)
# g.addEdge('d', 'b', 1)

# g = Graph()
# g.addEdge('a', ('b', -1))
# g.addEdge('a', ('c', 4))
# g.addEdge('b', ('c', 3))
# g.addEdge('b', ('d', 2))
# g.addEdge('b', ('e', 2))
# g.addEdge('d', ('c', 5))
# g.addEdge('d', ('b', 1))
# g.addEdge('e', ('d', -3))
# 
# g.BellmanFord('a')

g2 = Graph()
g2.createFromCsv('/Users/gregmurray/Documents/BigData/movie_rec_engine/ratings_sample.csv')
g2.BellmanFord('a')

fpath ='/Users/gregmurray/Documents/BigData/movie_rec_engine/ratings_sample.csv'
df = pd.read_csv(fpath)