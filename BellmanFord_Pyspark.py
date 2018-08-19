
#Author: Greg Murray
#Title: Bellman-Ford Recommendation Engine
#sc2 = spark.sparkContext 


class SparkGraph:
    def __init__(self, rdd):
            rdd2 = rdd.map(lambda x: (x[1][0], (x[0], -1*x[1][1])))
            rdd3 = rdd.union(rdd2)
            #7 times faster with 7 partitions opposed to 36
            #self.graph_rdd = rdd3.repartition(7) #change to 1 core for test printing
            self.graph_rdd = rdd3
            self.nodes = []
            self.top_recs = []
            self.dist = {}
            self.iters = 0
            self.times = {'rdd1':0, 'min_i':0, 'g.dist':0, 'broadcast':0}
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
    #def excludeSourceSeen(self):
        

#@parameter g: a SparkGraph object
#@parameter src: the key ID of the node from which to calculate distance
#@parameter g: a SparkGraph object
#optional @parameter degree penalty: a SparkGraph object
def bellmanFord(g, src, n, dgr_pen=1):
    import time
    g.setDist(src)
    dist = g.dist
    def compare_vs(x):
            d_v = dist.get(x[1][0], float("Inf"))
            d_u = dist.get(x[0], float("Inf"))
            w = x[1][1]
            if abs(d_u)<1:
                if d_u<0 and x[0]!=src:
                    d_u-=1
                elif x[0]!=src:
                    d_u+=1
            if abs(d_v)<1:
                if d_v<0 and x[1][0]!=src:
                    d_v-=1
                elif x[1][0]!=src:
                    d_v+=1
            #print(x[0], x[1][0], w)
            #print('d_u:', d_u, 'd_v:', d_v)
            if abs(dgr_pen*(w+d_u))<abs(d_v):
                if x[0]==src:
                    #print('returning d_u+w:', d_u+w)
                    return (x[1][0] , w+d_u)
                else:
                    #print('d_u', d_u)
                    #print('returning d_u+dp**w:', dgr_pen*(w+d_u))
                    return (x[1][0] , dgr_pen*(w+d_u))
            else:
                #print('returning d_v:', d_v)
                return (x[1][0], d_v)
    def test(x):
        return (x[1][0], x[1][1])
    def abs_min(a, b):
        if abs(a)<abs(b):
            return a
        else:
            return b
    for i in range(len(g.nodes)-1):
            g.iters +=1
            t = time.time()
            #dist = sc.broadcast(g.dist)
            times = sc.broadcast(g.times)
 
            t = time.time()
            #rdd1 = g.graph_rdd.map(compare_vs)
            rdd1 = g.graph_rdd.map(test)
            g.times['rdd1'] = g.times['rdd1']+(time.time()-t)
            t = time.time()
            min_i = rdd1.reduceByKey(abs_min).collect()
            g.times['min_i'] = g.times['min_i']+(time.time()-t)
            t = time.time()
            g.dist = dict(min_i)
            g.times['g.dist'] = g.times['g.dist']+(time.time()-t)
            #print('g.dist', g.dist)
            
            # if i==(len(g.nodes)/2):
            #     g.snapshot = g.dist
    # for k in g.dist:
    #         g.dist[k] = abs(g.dist[k])
    return g.topRecommendations(n)
    

# l = [('a', ('b', 2)), ('b', ('c', -1)), ('c', ('d', 1)), ('d', ('e', 1)), ('a', ('e', -4))]
# l2 = sc.parallelize(l)
# g = SparkGraph(l2)
# bellmanFord(g, 'a', 2, 1.5)
# g.dist

# demonstrates the impact of the degree penalty parameter. Set relatively small 1.1, the shortest path to 'c'
# utilizes more nodes a-e-d-c (remember negative the inverse pairs are negatively weighted) rather than
# a-b-c. Turning the degree penalty up to 1.5 and the shortest path becomes

g = SparkGraph(USER_MOVIE_NETWORK)
bellmanFord(g,'1', 5, 1)

real_func_times = copy.copy(g.times)
real_func_times['iters'] = copy.copy(g.iters)
real_func2_times = copy.copy(g.times)
real_func2_times['iters'] = copy.copy(g.iters)
part7_func_times = copy.copy(g.times)
part7_func_times['iters'] = copy.copy(g.iters)
test_func_times = copy.copy(g.times)
test_func_times['iters'] = copy.copy(g.iters)
