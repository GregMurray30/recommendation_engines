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

#(user, (movie, rating)
rt2 = rt.map(lambda x: (x[0], (x[1], x[2])))
nr = rt2.map(lambda x: (x[0], 1))
numRatings = nr.reduceByKey(lambda x,y: x+y)

#(movie, (user, rating)
rt3 = rt2.map(lambda x: (x[1][0], (x[0], x[1][1])))
rt4 = rt3.join(rt3)
rt5 = rt4.filter(lambda x: int(x[1][0][0])<int(x[1][1][0]))

# ((userA, userB), (ratingA, ratingB))    
rt6 = rt5.map(lambda x: ((x[1][0][0],x[1][1][0]),((float(x[1][0][1]), float(x[1][1][1])))))
rt7 = rt6.combineByKey(li, app, ext)
rt8 = rt7.map(lambda x: (x[0][0], (x[0], x[1])))
rt9=rt8.join(numRatings)
rt10 = rt9.map(lambda x: (x[1][0][0][1], x[1])) 
rt11=rt10.join(numRatings)


#rdd user_pairs object schema:
#[(user_A, user_B), ((num ratings user_A, num ratings user_B), [(user_A_rating_1, #user_B_rating_1), #(user_A_rating_2, user_B_rating_2),…, (user_A_rating_n, #user_B_rating_n)]))
user_pairs = rt11.map(lambda x: (x[1][0][0][0], ((x[1][0][1], x[1][1]), x[1][0][0][1]))).persist(storageLevel=StorageLevel.MEMORY_AND_DISK)


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

     
rate_diff1 = user_pairs.map(lambda x: (x,sim(x[1][1]))).persist(storageLevel=StorageLevel.MEMORY_AND_DISK)
#rate_diff2 schema: ((userA, userB), (num_shared_movies, (num_ratings_userA, num_ratings_userB), (mag_avg_diff, net_avg_diff)))
rate_diff2= rate_diff1.map(lambda x: (x[0][0],(len(x[0][1][1]),x[0][1][0], x[1])))


#shared_movies1 schema: (((userA, num_ratings_userA), ((userB, num_ratings_userB), ((mag_diffAB, net_diffAB), num_shared_movies))
shared_movies1 = rate_diff2.map(lambda x: ((x[0][0],x[1][1][0]),((x[0][1],x[1][1][1]),((x[1][2],x[1][0])))))
#shared_movies2 schema:(((userA, num_ratings_userA), ((userB, num_ratings_userB), ((mag_diffAB, -1*net_diffAB), num_shared_movies))
shared_movies2 = rate_diff2.map(lambda x: ((x[0][1],x[1][1][1]),((x[0][0],x[1][1][0]),((x[1][2][0], (-1)*x[1][2][1]),x[1][0]))))

shared_movies3 = shared_movies1.union(shared_movies2)

shared_movies4 = shared_movies3.combineByKey(li, app, ext)
#shared_movies_ schema: (((userA, num_ratings_userA), (userB, num_ratings_userB)), ((mag_diffAB, net_diffAB), num_shared_movies))
shared_movies_= shared_movies4.filter(lambda x: len(x[1])>1)


#USER NETWORK
#similar_user_pairs schema: (((userA, num_ratings_userA), (userB, num_ratings_userB)), ((mag_diffAB, net_diffAB), num_shared_movies))
similar_user_pairs = shared_movies1.map(lambda x: ((x[0], x[1][0]), x[1][1] ))

#edge_list schema:(userA, (userB, avg_net_diffAB))
edge_list=similar_user_pairs.map(lambda x: (x[0][0][0], (x[0][1][0], x[1][0][1])))