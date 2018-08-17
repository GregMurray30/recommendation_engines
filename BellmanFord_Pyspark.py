

#Author: Greg Murray
#Title: Bellman-Ford Recommendation Engine

class SparkGraph:
    def __init__(self, rdd):
            rdd2 = rdd.map(lambda x: (x[1][0], (x[0], -1*x[1][1])))
            rdd3 = rdd.union(rdd2)
            self.graph_rdd = rdd3
            self.nodes = []
            self.top_recs = []
            self.dist = {}
    def setVertices(self):
            rdd2 = self.graph_rdd.flatMap(lambda x: (x[0], x[1][0]))
            rdd3 = rdd2.map(lambda x: (x, 1))
            self.nodes = rdd3.reduceByKey(lambda a,b: a+b).map(lambda x: x[0]).collect()
    def setDist(self, source):
            self.setVertices()
            for n in self.nodes:
                    self.dist[n] = float("Inf")
                    self.dist[source]= 0
    def topRecommendations(self, n):
            self.top_recs = sorted(self.dist, key=self.dist.get)
            if n> len(self.dist):
                    return self.top_recs
            return self.top_recs[0:n]


def bellmanFord(g, src, n):
    g.setDist(src)
    def abs_min(a, b):
        if abs(a)<abs(b):
            return a
        else:
            return b
    for i in range(len(g.nodes)-1):
            dist = sc.broadcast(g.dist)
            rdd1 = g.graph_rdd.map(lambda x: (x[1][0] , dist.value.get(x[0], float("Inf"))+x[1][1]) if abs(dist.value.get(x[0], float("Inf"))+x[1][1])< abs(dist.value.get(x[1][0], float("Inf"))) else (x[1][0], dist.value.get(x[1][0], float("Inf"))) )
            #r = rdd1.collect()
            #print(r)
            min_i = rdd1.reduceByKey(abs_min).collect()
            g.dist = dict(min_i)
            #print('g.dist', g.dist)
    for k in g.dist:
            g.dist[k] = abs(g.dist[k])
    return g.topRecommendations(n)


g = SparkGraph(USER_MOVIE_NETWORK)
bellmanFord(g,'1', 3)
