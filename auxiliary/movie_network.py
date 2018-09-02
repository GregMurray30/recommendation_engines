# -*- coding: utf-8 -*-
from pyspark.storagelevel import StorageLevel
import math

rdd=sc.textFile('/Users/gregmurray/Documents/BigData/ratings_sample.txt').persist(storageLevel=StorageLevel.MEMORY_AND_DISK)


def li(v): return [v]

def app(a,b):
     a.append(b)
     return a

def ext(a,b):
     a.extend(b)
     return a
		
rt = rdd.map(lambda x: x.split("::"))
rt = rt.map(lambda x: x[0:3])

#(movie, (user, rating)
rt2 = rt.map(lambda x: (x[1], (x[0], x[2])))
nr = rt2.map(lambda x: (x[0], 1))
numRaters = nr.reduceByKey(lambda x,y: x+y)

#(user, (movie, rating)
rt3 = rt2.map(lambda x: (x[1][0], (x[0], x[1][1])))
rt4 = rt3.join(rt3)
rt5 = rt4.filter(lambda x: int(x[1][0][0])<int(x[1][1][0]))

# ((movieA, movieB), (ratingA, ratingB))   
rt6 = rt5.map(lambda x: ((x[1][0][0],x[1][1][0]),((float(x[1][0][1]), float(x[1][1][1])))))
rt7 = rt6.combineByKey(li, app, ext)
rt8 = rt7.map(lambda x: (x[0][0], (x[0], x[1])))
rt9=rt8.join(numRaters)
rt10 = rt9.map(lambda x: (x[1][0][0][1], x[1])) 
rt11=rt10.join(numRaters)


#rdd user_pairs object schema:
#[(movieA, movieB), ((num_raters_movie_A, num_raters_movie_B), [(movieA_rating_1, movieB_rating_1),
#(movieA_rating_2, movieB_rating_2),…, (movieA_rating_n, movieB_rating_n)]))
movie_pairs = rt11.map(lambda x: (x[1][0][0][0], ((x[1][0][1], x[1][1]), x[1][0][0][1]))).persist(storageLevel=StorageLevel.MEMORY_AND_DISK)


#Similarity Statistics
#Average rating difference

def sim(arr):
     d=0
     d2=0
     for pair in arr:
             d = d+(abs(pair[0]-pair[1]))
	     d2 = d2+(pair[0]-pair[1])
     d=d/(len(arr))
     d2=d2/(len(arr))
     d=round(d,2)
     d2=round(d2,2)
     return (d, d2)

     
rate_diff1 = movie_pairs.map(lambda x: (x,sim(x[1][1]))).persist(storageLevel=StorageLevel.MEMORY_AND_DISK)
#rate_diff2 schema: ((movieA, movieB), (num_shared_users, (num_raters_movieA, num_raters_movieB), (mag_avg_diff, avg_net_diff)))
rate_diff2= rate_diff1.map(lambda x: (x[0][0],(len(x[0][1][1]),x[0][1][0], x[1])))


#shared_users1 schema: (((movieA, num_raters_movieA), ((movieB, num_raters_movieB), ((mag_diffAB, net_diffAB), num_shared_users)
shared_users1 = rate_diff2.map(lambda x: ((x[0][0],x[1][1][0]),((x[0][1],x[1][1][1]),((x[1][2],x[1][0])))))
#shared_users2 schema:(((movieB, num_raters_movieB), ((movieA, num_raters_movieA), ((mag_diffAB, net_diffAB), num_shared_users)
shared_users2 = rate_diff2.map(lambda x: ((x[0][1],x[1][1][1]),((x[0][0],x[1][1][0]),((x[1][2][0], (-1)*x[1][2][1]),x[1][0]))))

shared_users3 = shared_movies1.union(shared_movies2)

shared_users4 = shared_movies3.combineByKey(li, app, ext)
#shared_users_ schema: (((movieA, num_raters_movieA), (movieB, num_raters_movieB)), ((mag_diffAB, net_diffAB), num_shared_users))
shared_users_= shared_movies4.filter(lambda x: len(x[1])>1)


#MOVIE NETWORK
#similar_movie_pairs schema: (((movieA, num_raters_movieA), (movieB, num_raters_movieB)), ((mag_diffAB, net_diffAB), num_shared_users))
similar_movies_pairs = shared_users1.map(lambda x: ((x[0], x[1][0]), x[1][1] ))

#Add 'm' to each movie ID for 'movie'
#movie_network schema: ((movieA, 'm'), ((movieB, 'm'), avg_net_diffAB))
movie_network=similar_user_pairs.map(lambda x: ((x[0][0][0], 'm'), ((x[0][1][0], 'm'), x[1][0][1])))



