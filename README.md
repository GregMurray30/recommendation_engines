
# MODEL CONCEPTUAL FRAMEWORK 

## INTRODUCTION
There are two models used for determining recommendations for users, the scalar model ([USER_MOVIE_NETWORK.py](https://github.com/GregMurray30/recommendation_engines/blob/master/USER_MOVIE_NETWORK.py)), and the Gaussian model ([USER_MOVIE_NETWORK_gaussian.py](https://github.com/GregMurray30/recommendation_engines/blob/master/USER_MOVIE_NETWORK_gaussian.py)). Both the scalar  and Gaussian network models
utilize basic network theory and Dijkstra's shortest path algorithm to generate movie[<sup>1</sup>](#1) recommendations.

The user-movie network has two node types, and is a weighted, non-directed and cyclic graph consisting
of two principal network node types, user and movie nodes, with node centrality in a skewed normal or 
power-law-like distribution.

<p align="center">
  <img src="https://github.com/GregMurray30/recommendation_engines/blob/master/visualizations/node_dist.png" title="Node Distribution">
 </p>
 
**Figure 1:** *A plot of node centrality distribution for a sample of ratings data with count of node connections on the x axis and density (count of nodes) on the y axis. Note that the count of node connections follows a skewed normal distribution in this sample.*

## SCALAR NETWORK MODEL:
The user nodes represent individual users. The network's edge weights are
calculated as the average magnitudinal difference of their shared-movie ratings. The weights are
non-directed and positive. As it is non-directed, the user node pairs still show up twice (*A-B* and *B-A*) 
in the graph's edge list where **w<sub>AB</sub>=(w<sub>*BA</sub>)**.

The movie nodes represent individual movies. Reciprocating the user nodes, the
movie network's edge weights are the average magnitudinal difference in their shared-user
ratings. 

Cross edges connecting a user node to a movie node indicate the user's rating of that movie
where node **u ∈ G<sub>user</sub>**, and node **v ∈ G<sub>movie</sub>**. In order for a high rating 
to correspond to a small distance, a rating-rank is used in (rating of 5 is a 1, rating of 4 
is 2, etc.) for the edge weight in place of the actual rating.

In order to accommodate a belief that an increase in degree separation should correspond to 
a decrease in the similarity regardless of the values of the edge weights, a weighting 
parameter **λ** is added to the distance function, *δ(E)*; compounding the the distance for each node traversal originating from the same node type. Formally, 
  
  > **δ(E<sub>uv</sub>; λ) = λE<sub>uv</sub>, where N<sub>x</sub> is node type x, and where N<sub>u</sub>=N<sub>v</sub>.**

Finally, movie recommendations are generated by ranking the user-to-movie traversals by shortest distances.

One of the advantages of using a dual-node-type network model is that the user's movie
ratings, her similarity to other users, and her rated movies' similarities to other
movies are not considered in any arbitrary order, but rather assessed simultaneously[<sup>2</sup>](#2). 
In addition, each node type's edge distances may be weighted according to one's beliefs about the impact 
that particular type*.

## GAUSSIAN NETWORK MODEL:

The Gaussian network model is identical to the scalar network except for the calculation of the
edge weight distances. Where the edge weights in the scalar model are simply the mean magnitude
of the rating differences, the Gaussian model's edge weights are the probability that the
difference between two users, or two movies, is greater than some designated threshold parameter **θ**.

<p align="center">
  <img src="https://github.com/GregMurray30/recommendation_engines/blob/master/visualizations/network_ex.png" title="Network_Example">
 </p>
 
**Figure 2:** *A representation of the Gaussian Network model. The varying thicknesses of each edge line represent different probabilities of similarity. Notice that the movie and user networks are not two separate clusters, but rather an mesh of the two node types inextricably linked by their complex relational edges.*
 
One major disadvantage of this approach is that the cumulative distribution function cannot be calculated 
for a sample with variance of zero. This becomes an issue with small sample sizes. In these instances, and 
where the mean difference is less than the threshold parameter **θ**, distance is calculated using a scaled version of the logistic function, *δ(n)=(1000+e<sup>n</sup>)/e<sup>n</sup>*, where **n** is the sample size. In the case where the mean difference is greater than the threshold parameter and the variance is zero, the edge is set equal to infinity, effectively removing the two nodes' connection from the network. Formally, distance in this network is calculated where
  
  >**δ(E<sub>uv</sub>; θ)=Pr[N(μ<sub>uv</sub>, σ<sub>uv</sub>)>θ]), when σ<sub>uv</sub>>0 and μ<sub>uv</sub><=θ;**
  
  >**δ(E<sub>uv</sub>; θ)=(1000+e<sup>n</sup>)/e<sup>n<sub>uv</uv></sup>, where n is the sample size of E<sub>uv</sub>, when σ<sub>uv</sub>=0 and μ<sub>uv</sub><=θ;**
  
  >**δ(E<sub>uv</sub>; θ)= ∞, otherwise**

Despite its longer convergence times (and admittedly "hacky" solution to zero-variance samples), the Guassian model retains one distinct advantage over its scalar counterpart: edge distances account for any uncertainty due to high variance in the sample of shared ratings. This frequently results in more sensible recommendations than the scalar model (although some of the recommendations frequently appear in both models). 

>###### 1
>*While movies are the recommendation object of interest in these examples, the model is generalizable to any data set that fits a user-product-rating paradigm. 

>###### 2
>*In this iteration of the scalar model the distances in the user network, movie network, and the
 user-movie cross network are scaled the same, assigning each network equal impact on the
 final recommendation. These edge weights could easily be scaled to accomodate one's
 beliefs on the importance each network has in determining the right movie recommendation.
 For instance if one believed that movie similarity was more important than user
 similarity, the edge weights in the movie network plane could be scaled down by some
 factor.*

