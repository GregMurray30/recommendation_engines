
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
            self.top_recs = sorted(sef.dist, key=self.dist.get)
            if n> len(self.dist):
                    return self.top_recs
            return self.top_recs[1:n+1]
    def printSelf(self):
            for k, v in self.dist:
                    print(k, v)
    

def BellmanFord(g, src):
    g.setDist(src)
    def abs_min(a, b):
        if abs(a)<abs(b):
            return a
        else:
            return b
    for i in range(len(g.nodes)-1):
            dist = sc.broadcast(g.dist)
            rdd1 = g.graph_rdd.map( lambda x: (x[1][0] , dist.value.get(x[0], float("Inf"))+x[1][1]) if abs(dist.value.get(x[0], float("Inf"))+x[1][1])< abs(dist.value.get(x[1][0], float("Inf"))) else (x[1][0],dist.value.get(x[1][0], float("Inf"))) )
            min_i = rdd1.reduceByKey(abs_min).collect()
            g.dist = dict(min_i)
            print('g.dist', g.dist)
    for k in g.dist:
            g.dist[k] = abs(g.dist[k])



l=[('a', ('b', 3)),  ('b', ('c', 1)),  ('c', ('d', -4)) ,('d', ('e', 3)), ('e', ('f', 1))]
l = [("a",  ("b",4)),("a",  ("c",3)),("b",  ("c",2)),("b",  ("f",-1)),("a",  ("g",-2)),
("a",  ("f",3)),("b",  ("d",3)),("c",  ("d",2)),("h",  ("b",1)),("g",  ("d",-2)), ("c", ("h", -4))]

l = [("a",  ("c",3)),("b",  ("c",2)),("b",  ("f",-1)),
("a",  ("f",3)),("b",  ("d",3)),("c",  ("d",2)),("h",  ("b",1)),("g",  ("d",-2)), ("c", ("h", -4))]
l2= sc.parallelize(l)
g = SparkGraph(l2)
BellmanFord(g,'a')

ac
