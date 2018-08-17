# -*- coding: utf-8 -*-
from pyspark.storagelevel impou_rt StorageLevel
impou_rt math

rdd=sc.textFile('/Users/gregmurray/Documents/BigData/movie_rec_eng/ratings_sample_small.txt').persist(storageLevel=StorageLevel.MEMORY_AND_DISK)


def li(v): return [v]

def app(a,b):
     a.append(b)
     return a

def ext(a,b):
     a.extend(b)
     return a
		
rt = rdd.map(lambda x: x.split("::"))
rt = rt.map(lambda x: x[0:3])

#______________________________________________________________________________#
#USER NETWORK

#(user, (movie, rating)
u_rt2 = rt.map(lambda x: (x[0], (x[1], x[2])))
u_nr = u_rt2.map(lambda x: (x[0], 1))
numRatings = u_nr.reduceByKey(lambda x,y: x+y)

#(movie, (user, rating)
u_rt3 = u_rt2.map(lambda x: (x[1][0], (x[0], x[1][1])))
u_rt4 = u_rt3.join(u_rt3)
u_rt5 = u_rt4.filter(lambda x: int(x[1][0][0])<int(x[1][1][0]))

# ((userA, userB), (ratingA, ratingB))    
u_rt6 = u_rt5.map(lambda x: ((x[1][0][0],x[1][1][0]),((float(x[1][0][1]), float(x[1][1][1])))))
u_rt7 = u_rt6.combineByKey(li, app, ext)
u_rt8 = u_rt7.map(lambda x: (x[0][0], (x[0], x[1])))
u_rt9=u_rt8.join(numRatings)
u_rt10 = u_rt9.map(lambda x: (x[1][0][0][1], x[1])) 
u_rt11=u_rt10.join(numRatings)

#rdd user_pairs object schema:
#[(user_A, user_B), ((num ratings user_A, num ratings user_B), [(user_A_rating_1, #user_B_rating_1), #(user_A_rating_2, user_B_rating_2),…, (user_A_rating_n, #user_B_rating_n)]))
user_pairs = u_rt11.map(lambda x: (x[1][0][0][0], ((x[1][0][1], x[1][1]), x[1][0][0][1]))).persist(storageLevel=StorageLevel.MEMORY_AND_DISK)

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

u_rate_diff1 = user_pairs.map(lambda x: (x,sim(x[1][1]))).persist(storageLevel=StorageLevel.MEMORY_AND_DISK)
#rate_diff2 schema: ((userA, userB), (num_shared_movies, (num_ratings_userA, num_ratings_userB), (mag_avg_diff, net_avg_diff)))
u_rate_diff2= u_rate_diff1.map(lambda x: (x[0][0],(len(x[0][1][1]),x[0][1][0], x[1])))

#shared_movies1 schema: (((userA, num_ratings_userA), ((userB, num_ratings_userB), ((mag_diffAB, net_diffAB), num_shared_movies))
shared_movies1 = u_rate_diff2.map(lambda x: ((x[0][0],x[1][1][0]),((x[0][1],x[1][1][1]),((x[1][2],x[1][0])))))

#shared_movies 2-4 are for future iterations when more advanced metrics are used rather than just mean
# #shared_movies2 schema:(((userA, num_ratings_userA), ((userB, num_ratings_userB), ((mag_diffAB, -1*net_diffAB), num_shared_movies))
# shared_movies2 = u_rate_diff2.map(lambda x: ((x[0][1],x[1][1][1]),((x[0][0],x[1][1][0]),((x[1][2][0], (-1)*x[1][2][1]),x[1][0]))))
# shared_movies3 = shared_movies1.union(shared_movies2)
# shared_movies4 = shared_movies3.combineByKey(li, app, ext)
# #shared_movies_ schema: (((userA, num_ratings_userA), (userB, num_ratings_userB)), ((mag_diffAB, net_diffAB), num_shared_movies))
# shared_movies_= shared_movies4.filter(lambda x: len(x[1])>1)

#similar_user_pairs schema: (((userA, num_ratings_userA), (userB, num_ratings_userB)), ((mag_diffAB, net_diffAB), num_shared_movies))
similar_user_pairs = shared_movies1.map(lambda x: ((x[0], x[1][0]), x[1][1] ))


#Add 'u' to each user ID for 'user'
#USER_NETWORK schema:(userA, (userB, avg_net_diffAB))
USER_NETWORK = similar_user_pairs.map(lambda x: ((x[0][0][0], 'u'), ((x[0][1][0], 'u'), x[1][0][1])))


#______________________________________________________________________________#
#MOVIE NETWORK
#(movie, (user, rating)
def rating_rank(v):
    if float(v[1])>4.5: #rating of 5
        return (v[0], 0.0)
    elif float(v[1])>4.0:
        return (v[0], 0.5)
    elif float(v[1])>3.5:
        return (v[0], 1.0)
    elif float(v[1])>3.0:
        return (v[0], 1.5)
    elif float(v[1])>2.5:
        return (v[0], 2.0)
    elif float(v[1])>2.0:
        return (v[0], 2.5)
    elif float(v[1])>1.5:
        return (v[0], 3.0)
    elif float(v[1])>1.0:
        return (v[0], 3.5)
    elif float(v[1])>0.5:
        return (v[0], 4.0)
    elif float(v[1])>0.0:
        return (v[0], 4.5)
        
        
m_rt1 = rt.map(lambda x: (x[1], (x[0], x[2])))
m_rt2 = m_rt1.mapValues(rating_rank)
m_nr = m_rt2.map(lambda x: (x[0], 1))
numRaters = m_nr.reduceByKey(lambda x,y: x+y)

#(user, (movie, rating)
m_rt3 = m_rt2.map(lambda x: (x[1][0], (x[0], x[1][1])))
m_rt4 = m_rt3.join(m_rt3)
m_rt5 = m_rt4.filter(lambda x: int(x[1][0][0])<int(x[1][1][0]))

# ((movieA, movieB), (ratingA, ratingB))   
m_rt6 = m_rt5.map(lambda x: ((x[1][0][0],x[1][1][0]),((float(x[1][0][1]), float(x[1][1][1])))))
m_rt7 = m_rt6.combineByKey(li, app, ext)
m_rt8 = m_rt7.map(lambda x: (x[0][0], (x[0], x[1])))
m_rt9=m_rt8.join(numRaters)
m_rt10 = m_rt9.map(lambda x: (x[1][0][0][1], x[1])) 
m_rt11=m_rt10.join(numRaters)

#rdd user_pairs object schema:
#[(movieA, movieB), ((num_raters_movie_A, num_raters_movie_B), [(movieA_rating_1, movieB_rating_1),
#(movieA_rating_2, movieB_rating_2),…, (movieA_rating_n, movieB_rating_n)]))
movie_pairs = m_rt11.map(lambda x: (x[1][0][0][0], ((x[1][0][1], x[1][1]), x[1][0][0][1]))).persist(storageLevel=StorageLevel.MEMORY_AND_DISK)

m_rate_diff1 = movie_pairs.map(lambda x: (x,sim(x[1][1]))).persist(storageLevel=StorageLevel.MEMORY_AND_DISK)
#rate_diff2 schema: ((movieA, movieB), (num_shared_users, (num_raters_movieA, num_raters_movieB), (mag_avg_diff, avg_net_diff)))
m_rate_diff2= m_rate_diff1.map(lambda x: (x[0][0],(len(x[0][1][1]),x[0][1][0], x[1])))

#shared_users1 schema: (((movieA, num_raters_movieA), ((movieB, num_raters_movieB), ((mag_diffAB, net_diffAB), num_shared_users)
shared_users1 = m_rate_diff2.map(lambda x: ((x[0][0],x[1][1][0]),((x[0][1],x[1][1][1]),((x[1][2],x[1][0])))))

#shared_users 2-4 are for future iterations when more advanced metrics are used rather than just mean
# #shared_users2 schema:(((movieB, num_raters_movieB), ((movieA, num_raters_movieA), ((mag_diffAB, net_diffAB), num_shared_users)
# shared_users2 = m_rate_diff2.map(lambda x: ((x[0][1],x[1][1][1]),((x[0][0],x[1][1][0]),((x[1][2][0], (-1)*x[1][2][1]),x[1][0]))))
# shared_users3 = shared_users1.union(shared_movies2)
# shared_users4 = shared_users3.combineByKey(li, app, ext)
# #shared_users_ schema: (((movieA, num_raters_movieA), (movieB, num_raters_movieB)), ((mag_diffAB, net_diffAB), num_shared_users))
# shared_users_= shared_users4.filter(lambda x: len(x[1])>1)

#similar_movie_pairs schema: (((movieA, num_raters_movieA), (movieB, num_raters_movieB)), ((mag_diffAB, net_diffAB), num_shared_users))
similar_movie_pairs = shared_users1.map(lambda x: ((x[0], x[1][0]), x[1][1] ))


#Add 'm' to each movie ID for 'movie'
#MOVIE_NETWORK schema: ((movieA, 'm'), ((movieB, 'm'), avg_net_diffAB))
MOVIE_NETWORK = similar_movie_pairs.map(lambda x: ((x[0][0][0], 'm'), ((x[0][1][0], 'm'), x[1][0][1])))


#______________________________________________________________________________#
#USER-MOVIE NETWORK

###Final User-Movie Network RDD
USER_MOVIE_NETWORK = USER_NETWORK.union(MOVIE_NETWORK)