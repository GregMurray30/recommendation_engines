#Author: Greg Murray
#Title: Bellman-Ford Recommendation Engine
#sc2 = spark.sparkContext 

#sc = spark.sparkContext
class SparkGraph:
    def __init__(self, rdd):
            rdd2 = rdd.map(lambda x: (x[1][0], (x[0], -1*x[1][1])))
            rdd3 = rdd.union(rdd2)
            #self.graph_rdd = rdd3.repartition(1)
            self.graph_rdd = rdd3
            self.nodes = []
            self.top_recs = []
            self.dist = {}
            self.iters = 0
            self.times = {'rdd1':0, 'min_i':0, 'g.dist':0}
            self.snapshot = None
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
    def excludeSourceSeen(self, src):
        src_seen = self.graph_rdd.filter(lambda x: x[0]==src).map(lambda x: x[1][0]).collect()
        src_seen = sc.broadcast(src_seen)
        dist_rdd = sc.parallelize(self.dist.items())
        g.dist = dict(dist_rdd.filter(lambda x: x[0] not in src_seen.value).collect())
        


def bellmanFord(g, src, n, degree_penalty=1):
    import time
    g.setDist(src)
    dgr_pen = sc.broadcast(degree_penalty)
    src_bc = sc.broadcast(src)
    def compare_vs(x):
            d_v = dist.value.get(x[1][0], float("Inf"))
            d_u = dist.value.get(x[0], float("Inf"))
            w = x[1][1]
            
            if abs(d_u)<1:
                if d_u<0 and x[0]!=src_bc.value:
                    d_u-=1
                elif x[0]!=src_bc.value:
                    d_u+=1
            if abs(d_v)<1:
                if d_v<0 and x[1][0]!=src_bc.value:
                    d_v-=1
                elif x[1][0]!=src_bc.value:
                    d_v+=1
            #print(x[0], x[1][0], w)
            #print('d_u:', d_u, 'd_v:', d_v)
            if abs(dgr_pen.value*(w+d_u))<abs(d_v):
                
                if x[0]==src_bc.value:
                    #print('returning d_u+w:', d_u+w)
                    return (x[1][0] , w+d_u)
                else:
                    #print('d_u', d_u)
                    #print('returning d_u+dp**w:', dgr_pen.value*(w+d_u))
                    return (x[1][0] , dgr_pen.value*(w+d_u))
            else:
                #print('returning d_v:', d_v)
                return (x[1][0], d_v)
    def abs_min(a, b):
        if abs(a)<abs(b):
            return a
        else:
            return b
    for i in range(len(g.nodes)-1):
            g.iters +=1
            dist = sc.broadcast(g.dist)
            rdd1 = g.graph_rdd.map(compare_vs)
            t = time.time()
            min_i = rdd1.reduceByKey(abs_min).collect()
            g.times['min_i'] = g.times['min_i']+(time.time()-t)
            g.dist = dict(min_i)
            #print('g.dist', g.dist)
            if i==(len(g.nodes)/2):
                g.snapshot = g.dist
    # for k in g.dist:
    #         g.dist[k] = abs(g.dist[k])
    g.excludeSourceSeen(src)
    return g.topRecommendations(n)
    

# l = [('a', ('b', -3)), ('b', ('c', 1)), ('c', ('d', 1)), ('d', ('e', 1)), ('a', ('e', -3))]
# l2 = sc.parallelize(l)
# g = SparkGraph(l2)
# bellmanFord(g, 'a', 2, 1.1)
# g.dist

# demonstrates the impact of the degree penalty parameter. Set relatively small 1.1, the shortest path to 'c'
# utilizes more nodes a-e-d-c (remember negative the inverse pairs are negatively weighted) rather than
# a-b-c. Turning the degree penalty up to 1.5 and the shortest path becomes

g = SparkGraph(USER_MOVIE_NETWORK)
bellmanFord(g,'1', 5, 1.1)
