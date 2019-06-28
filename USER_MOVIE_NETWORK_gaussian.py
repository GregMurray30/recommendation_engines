# -*- coding: utf-8 -*-
#Author: Greg Murray
#Title: Gaussian User-Movie Network Recommendation Engine

from pyspark.storagelevel import StorageLevel
import math

sc = spark.sparkContext

rdd=sc.textFile('/Users/gregmurray/Documents/BigData/movie_rec_engine/Final_Package/data_sources/ratings_sample_tiny.csv').persist(storageLevel=StorageLevel.MEMORY_AND_DISK)
rdd=rdd.filter(lambda x: x[0]!='user_id')
rt = rdd.map(lambda x: x.split(","))
rt = rt.map(lambda x: x[0:3])

#______________________________________________________________________________#
#Functions
def li(v): return [v]


def app(a,b):
     a.append(b)
     return a

def ext(a,b):
     a.extend(b)
     return a


#standard deviation of each user
import statistics as st
def sd1(v):
	if len(v[1])==1:
		return (v, 0)
	else:
		return (v, round(st.stdev(v[1]),3))
	
#mean of each movie or user. 
def mean(v):
	if len(v[0][1])==1:
		return (v[0][0], (v[0][1][0], v[1]))
	else:
		return ( v[0][0], (round(st.mean(v[0][1]),3), v[1]) )	
	
#get weighted rating-difference value (wrdv)
def get_wrdv(arr, gamma=.25, alpha=1, b=1):
	res=[]
	for tup in arr:
		r_u = tup[0][0]
		r_v = tup[0][1]
		x_mean = tup[1][0]
		x_sd = tup[1][1]
		wrdv_numerator = 1+abs(r_u-r_v)*(abs(r_u-r_v)**.5)
		wrdv_denominator = ((alpha*(gamma+(r_v-x_mean)**2)**.5)*(gamma+(r_u-x_mean)**2)**.5)**.5
		wrdv = round(wrdv_numerator/wrdv_denominator, 3)
		res.append(wrdv)
	return res

#get probability that 
def get_prob(arr):
	res=[]
	for tup in arr:
		wrdv = round((1+abs(tup[0][0]-tup[0][1]))/(1+tup[1]), 3)
		res.append(wrdv)
	return res



import scipy.stats as ss
import math
def prob_pairs(theta):
    def _prob_pairs(v):
        prob = float(ss.norm(v[0], v[1]).cdf(theta)) #probability difference < theta (where theta is the threshold param)
        #if variance==0 then hack a probability estimate with logistic func if the mean <=1
        if math.isnan(prob):
            if v[0]<=theta:
                prob=1-(math.exp(v[1])/(1000+math.exp(v[1])))
                return ((v[0], v[1]), round(prob, 3))
            else:
                prob=0
                return ((v[0], v[1]), prob)
        return ((v[0], v[1]), round(prob, 3))
    return _prob_pairs


#______________________________________________________________________________#
#USER NETWORK

#(user, (movie, rating)
u_rt2 = rt.map(lambda x: (x[0], (x[1], x[2])))

#(movie, (user, rating)
u_rt3 = u_rt2.map(lambda x: (x[1][0], (x[0], float(x[1][1]))))

#sd5b:(u'4999', (4.0, (u'657', 4.0)))]
#sd5: (u'4999', (0, (u'657', 4.0)))
	
#standard deviation of users
u_sd1 = u_rt3.mapValues(lambda x: x[1])
u_sd2 = u_sd1.combineByKey(li, app, ext)
u_sd3 = u_sd2.map(sd1)
u_sd3b = u_sd3.map(mean)
#u_sd4 = u_sd3b.map(lambda x: (x[0], (x[1], x[0][1])))
u_sd5 = u_sd3b.join(u_rt3)
u_sd6 = u_sd5.map(lambda x: ((x[0], x[1][0]), x[1][1]))

#u_rt5 schema: ((movie, (movie_mean, movie_stdev)), (userA, ratingA), (userB, ratingB))
u_rt4 = u_sd6.join(u_sd6)
u_rt5 = u_rt4.filter(lambda x: int(x[1][0][0])<int(x[1][1][0]))
# u_rt6 schema: ((userA, userB), (ratingA, ratingB), (movie_mean, movie_stdev))   
u_rt6 = u_rt5.map(lambda x: ((x[1][0][0],x[1][1][0]), ((x[1][0][1], x[1][1][1]), x[0][1])))

#rdd user_pairs object schema:
#((userA, userB), ([((userA_rating1, userB_rating_1), (movie1_mean, movie1_stdev),
#((userA_rating_2, userB_rating_2), movie2_stdev),…, ((userA_rating_n, userB_rating_n), movie_n_stdev)]))
user_pairs1 = u_rt6.combineByKey(li, app, ext)

#user_pairs2 schema: ((userA, userB), [wrdv1, wrdv_2,...,wrdv_n])
user_pairs2 = user_pairs1.mapValues(get_wrdv)
user_pairs3 = user_pairs2.map(sd1)

#user_pairs4 schema: (((userA, userB), (avg_wrdv, sd_wrdv), num_shared_movies))
user_pairs4 = user_pairs3.map(lambda x: (x[0][0], (round(st.mean(x[0][1]), 3), x[1]), len(x[0][1])))

#m_cdf_pairs schema: ((userA, movieB), (avg_mag_diffAB, sd_diffAB), sample_size), probability_diff<theta)
u_cdf_pairs = user_pairs4.mapValues(prob_pairs(1))

#Add 'u' to each movie ID for 'user'
#USER_NETWORK schema: ((userA, 'u'), ((userB, 'u'),  probability_wrdv<theta)
USER_NETWORK = u_cdf_pairs.map(lambda x: ((x[0][0], 'u'), ((x[0][1], 'u'), x[1][1])))


#______________________________________________________________________________#
#MOVIE NETWORK

#(movie, (user, rating)
m_rt2 = rt.map(lambda x: (x[1], (x[0], x[2])))

#(user, (movie, rating)
m_rt3 = m_rt2.map(lambda x: (x[1][0], (x[0], float(x[1][1]))))

#standard deviation of users
m_sd1 = m_rt3.mapValues(lambda x: x[1])
m_sd2 = m_sd1.combineByKey(li, app, ext)
m_sd3 = m_sd2.map(sd1)
m_sd4 = m_sd3.map(lambda x: (x[0][0], (x[1]), x[0][1]))
m_sd5 = m_sd4.join(m_rt3)
m_sd6 = m_sd5.map(lambda x: ((x[0], x[1][0]), x[1][1]))

#m_rt5 schema: ((user, user_stdev), (movieA, ratingA), (movieB, ratingB))
m_rt4 = m_sd6.join(m_sd6)
m_rt5 = m_rt4.filter(lambda x: int(x[1][0][0])<int(x[1][1][0]))
# ((movieA, movieB), (ratingA, ratingB), user_stdev)   
m_rt6 = m_rt5.map(lambda x: ((x[1][0][0],x[1][1][0]), ((x[1][0][1], x[1][1][1]), x[0][1])))

#rdd user_pairs object schema:
#[(movieA, movieB), ([((movieA_rating_1, movieB_rating_1), user1_stdev),
#((movieA_rating_2, movieB_rating_2), user2_stdev),…, ((movieA_rating_n, movieB_rating_n), usern_stdev)]))
movie_pairs1 = m_rt6.combineByKey(li, app, ext)
	
#movie_pairs2 schema: ((movieA, movieB), [weighted_rating_difference_value_1, weighted_rating_difference_value_2,...,weighted_rating_difference_value_n])
movie_pairs2 = movie_pairs1.mapValues(get_wrdv)
movie_pairs3 = movie_pairs2.map(sd1)

#movie_pairs4 schema: (((movieA, movieB), (avg_wrdv, sd_wrdv), num_shared_users))
movie_pairs4 = movie_pairs3.map(lambda x: (x[0][0], (round(st.mean(x[0][1]), 3), x[1]), len(x[0][1])))

#m_cdf_pairs schema: ((movieA, 'm'), (movieB, 'm')), (avg_mag_diffAB, sd_diffAB), sample_size), probability_diff>theta)
m_cdf_pairs = movie_pairs4.mapValues(prob_pairs(1))

#Add 'm' to each movie ID for 'movie'
#MOVIE_NETWORK schema: ((movieA, 'm'), ((movieB, 'm'),  probability_wrdv>theta)
MOVIE_NETWORK = m_cdf_pairs.map(lambda x: ((x[0][0], 'm'), ((x[0][1], 'm'), x[1][1])))


#______________________________________________________________________________#
#USER-MOVIE NETWORK

###Final User-Movie Network RDD
def rating_rank(v):
    if float(v[1])>4.5: #rating of 5
        return (v[0], 1.0)
    elif float(v[1])>4.0:
        return (v[0], .95)
    elif float(v[1])>3.5:
        return (v[0], 0.85)
    elif float(v[1])>3.0:
        return (v[0], 0.75)
    elif float(v[1])>2.5:
        return (v[0], 0.55)
    elif float(v[1])>2.0:
        return (v[0], 0.4)
    elif float(v[1])>1.5:
        return (v[0], 0.3)
    elif float(v[1])>1.0:
        return (v[0], 0.2)
    elif float(v[1])>0.5:
        return (v[0], 0.1)
    elif float(v[1])>0.0:
        return (v[0], .05)
        

um_ratings = u_rt2.mapValues(rating_rank)
um_ratings2 = um_ratings.map(lambda x: ((x[0], 'u'), ((x[1][0], 'm'), x[1][1])))
user_movie_network0 = USER_NETWORK.union(MOVIE_NETWORK)

USER_MOVIE_NETWORK_Gaussian = user_movie_network0.union(um_ratings2)
