# recommendation_engines
Recommendation engines using Apache Spark
Ratings_sample.txt is "::" separated value file in the format [user_id]::[movie_id]::[rating]::[rating_date]. 

A movie is scored on 5 criteria in order of importance. The higher the score the higher that movie will be on the recommendation list. 
1.	Similar movie to one user has rated highly
2.	Rated highly by other users with whom the user of interest is tier1-similar (<1.25 avg magnitude of rating difference)
3.	Rated highly by other users with whom the user of interest is tier2-similar ("friend of my friend = my friend' ")
4.	Rated highly by other users with whom the user of interest is tier3-similar ("enemy of my enemy = my friend'' ")
5.	Movie overall rating

