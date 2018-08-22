#Author: Greg Murray
#Title: Bellman-Ford Recommendation Engine
#sc2 = spark.sparkContext 

#sc = spark.sparkContext
class SparkGraph:
    def __init__(self, rdd):
            #self.graph_rdd = rdd.repartition(1)
            self.graph_rdd = rdd
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
        #excludes movies user has already seen and non-movie nodes
        src_seen = self.graph_rdd.filter(lambda x: x[0]==src).map(lambda x: x[1][0]).collect()
        src_seen.append(src)
        src_seen = sc.broadcast(src_seen)
        dist_rdd = sc.parallelize(self.dist.items())
        self.dist = dict(dist_rdd.filter(lambda x: x[0] not in src_seen.value and x[0][1]=='m').collect())
    


def bellmanFord(g, src, n, degree_penalty=1):
    import time
    g.setDist(src)
    dgr_pen = sc.broadcast(degree_penalty)
    src_bc = sc.broadcast(src)
    def compare_vs(x):
            d_v = dist.value.get(x[1][0], float("Inf"))
            d_u = dist.value.get(x[0], float("Inf"))
            w = x[1][1]
            if x[0]!=src_bc.value and x[1][0]!=src_bc.value:
                w+=1
            #print(x[0], x[1][0], w)
            #print('d_u:', d_u, 'd_v:', d_v)
            if dgr_pen.value*w+d_u<d_v:
                #if u==source or u and v are in different network clusters
                if x[0]==src_bc.value or x[0][1]!=x[1][0][1]:
                    #print('returning d_u+w:', d_u+w)
                    return (x[1][0] , w+d_u)
                else:
                    #print('d_u', d_u)
                    #print('returning d_u+dp**w:', dgr_pen.value*(w+d_u))
                    return (x[1][0] , dgr_pen.value*w+d_u)
            else:
                #print('returning d_v:', d_v)
                return (x[1][0], d_v)
    def abs_min(a, b):
        if abs(a)<abs(b):
            return a
        else:
            return b
    for i in range(len(g.nodes)-1):
            g.iters+=1
            dist = sc.broadcast(g.dist)
            rdd1 = g.graph_rdd.map(compare_vs)
            t = time.time()
            min_i = rdd1.reduceByKey(abs_min).collect()
            g.times['min_i'] = g.times['min_i']+(time.time()-t)
            g.dist = dict(min_i)
            #print('g.dist', g.dist)
            if i==(len(g.nodes)/2):
                g.snapshot = g.dist
    g.excludeSourceSeen(src)
    return g.topRecommendations(n)
    


if __name__=="__main__":
    #g = SparkGraph(USER_MOVIE_NETWORK_Gaussian)
    s =  SparkGraph(USER_MOVIE_NETWORK)
    #bellmanFord(g,('1', 'u'), 5, 1.2)
    bellmanFord(s,('1', 'u'), 5, 1.2)
    
    #Lookup values in previous rdds for reference on the recommendations validity
    #g.graph_rdd.filter(lambda x: x[0]==('1', 'u') and x[1][0]==('2', 'u')).collect()
    s.graph_rdd.filter(lambda x: x[0]==('1', 'u') and x[1][0]==('8', 'u')).collect()
    
    u_cdf_pairs.filter(lambda x: x[0][0][0]=='1' and x[0][1][0]=='8').collect()
