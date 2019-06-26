# MODEL CONCEPTUAL FRAMEWORK 
>#### **by Greg Murray**

<p align="center">
  <img src="https://github.com/GregMurray30/recommendation_engines/blob/master/visualizations/network_ex2.png" title="Network_Example">
 </p>
 
**Figure 1:** *A representation of the [Gaussian Network Model](#Gaussian_Network_Model). The varying widths of the edge lines represent different probabilities of similarity. Notice that the item (movie) and user networks are not two separate clusters but rather a mesh of the two node types inextricably linked by their complex interchange of relational edges.*

## INTRODUCTION

The recommender system detailed in this paper is a collaborative filtering, hybrid model, employing components of user-based nearest neighbor and item-based nearest neighbor recommenders, basic network theory, and probability theory, implemented in a MapReduce framework. 

There are two models used for determining recommendations for users, the Pearson model ([USER_MOVIE_NETWORK.py](https://github.com/GregMurray30/recommendation_engines/blob/master/USER_MOVIE_NETWORK.py)), and the Gaussian model ([USER_MOVIE_NETWORK_gaussian.py](https://github.com/GregMurray30/recommendation_engines/blob/master/USER_MOVIE_NETWORK_gaussian.py)). Aside from their edge weightings, both the Pearson and Gaussian networks are modelled identically and
utilize a [spreading activation](https://github.com/GregMurray30/recommendation_engines/blob/master/Spreading_Activation.py) algorithm to assess the network efficiently and subsequently generate item recommendations.

The user-item network is a weighted, non-directed and acyclic graph<sup>[1](#1)</sup> consisting of two node types, user and item, with node centrality typically in a skewed normal or power-law-like distribution.

<p align="center">
  <img src="https://github.com/GregMurray30/recommendation_engines/blob/master/visualizations/node_dist.png" title="Node Distribution">
 </p>
 
**Figure 2:** *A plot of node centrality distribution for a sample of ratings data with count of node connections on the x axis and density on the y axis. Note that the count of node connections follows a positively skewed normal distribution in this sample.*

## PEARSON NETWORK MODEL

#### USER NODES
Each user node represents an individual user in this network model. The network's edge weights are
calculated as the Pearson correlation coefficient (hence the name) of the user pair's shared item ratings, as has been demonstrated as the most accurate measurement of similarity between users (Herlocker et al. 1999). For two users, X and Y, then, their sample similarity, *r*, is defined as 
![alt text](https://wikimedia.org/api/rest_v1/media/math/render/svg/bd1ccc2979b0fd1c1aec96e386f686ae874f9ec0).

#### ITEM NODES
The second type of node in this model is the item node which represents individual items. Reciprocating the user nodes, the
item network's edge weights are determined by the two item pair's shared user ratings, but this time using cosine similarity. For items A and B then, 
![alt text](https://wikimedia.org/api/rest_v1/media/math/render/svg/1d94e5903f7936d3c131e040ef2c51b473dd071d).

#### CROSS EDGES
Cross edges connecting a user node to a item node indicate the user's rating of that movie
where node **u ∈ G<sub>user</sub>**, and node **v ∈ G<sub>movie</sub>**. In order for a high rating 
to correspond to a small distance, a rating-rank (rating of 5->1, rating of 4->2, etc.) is used for the edge weight in place of the actual rating.

In order to accommodate a belief that an increase in degree of separation (as in Kevin Bacon) should correspond to 
a decrease in the similarity regardless of the values of the edge weights, a weighting 
parameter **λ** is added to the distance function, *δ(E)*; compounding the the distance for each node traversal originating from the same node type. Formally, 
  
  > **δ<sub>uv</sub>(E<sub>uv</sub>; λ) = λE<sub>uv</sub>**
 
where **nodeType<sub>u</sub>=nodeType<sub>v</sub>.**

## GAUSSIAN NETWORK MODEL

The Gaussian network model is identical to the Pearson model except for the calculation of the
edge weight distances. Where the edge weights in the Pearson model are calculated with the correlation coefficient and cosine similarity, the Gaussian model's edge weights are the probability that the weighted, average, magnitudinal
difference between two users, or two items, is less than some designated threshold parameter **θ**. Accordingly, the weighted rating-difference value (*wrdv*) function of each rating difference belonging to a node pair - not to be confused with the pair's edge distance - was engineered to exhibit properties that reflect the author's prior beliefs about each rating scenario's implications on similarity. The function contains two hyperparameters to control curvature, γ, and sensitivity, α, and σ-explosiveness, b. The wrdv function is defined, 

> **ω<sub>uv<sub>x</sub></sub>(r<sub>u<sub>x</sub></sub>, r<sub>v<sub>x</sub></sub>, σ<sub>x</sub>, r<sub>avg<sub>x</sub></sub>, γ, α)= (1+|r<sub>u<sub>x</sub></sub>-r<sub>v<sub>x</sub></sub>|)/
((α+(γ+(r<sub>u<sub>x</sub></sub>-r<sub>avg<sub>x</sub></sub>)^2)^.5)+(α+(γ+(r<sub>v<sub>x</sub></sub>-r<sub>avg<sub>x</sub></sub>)^2)^.5))(b+σ<sub>x</sub>)**

where *ω<sub>uv<sub>x</sub></sub>* is the wrdv of node pair *u-v* for item/user x, *r<sub>u<sub>x</sub></sub>* is node u's rating of item (or rating from user) x, and *r<sub>v<sub>x</sub></sub>* is node b's rating of item (or rating from user) x. 

<p align="center">
  <img src="https://github.com/GregMurray30/recommendation_engines/blob/master/visualizations/constant_rating3.png" title="Constant Rating Differences">
 </p>

**Figure 3a:** *The **wrdv** on the y axis plotted against the standard deviation (**σ**) on the x axis with param b=1, holding the mean rating of the item constant. Each curve represents a constant value for the rating difference and shows how the wrdv varies with the σ of the item's ratings. Note that *σ* has more impact on the wrdv when there is consensus opinion (σ is small) compared to when there are mixed reviews (σ is large), and that this effect is more dramatic in the "rating difference=4" curve (brown) than the "rating difference=0" (red) curve.*
 
  <p align="center">
  <img src="https://github.com/GregMurray30/recommendation_engines/blob/master/visualizations/mean_v_wrdv_1.png" title="Mean Rating X vs. WRDV: Slightly Divergent Ratings">
 </p>
 
  **Figure 3b:** *The **WRDV** on the y axis plotted against the mean rating of item x on the x axis with params α=1 and γ=.25, holding the standard deviation of the item constant. The blue and red curves reflect the effect on wrdv when the difference between the ratings is 2. The blue curve is when u and v rated 5 and 3, and the red curve is when u and v rated 3 and 1. **The belief is that a mildly positive rating paired with a strongly positive rating, when distinct from the mean rating of the item, indicates more similarity than when the mean rating is near the ratings of u and v (ie: r_u=5, r_v=3, r_avg_x=1 vs r_avg_x=4**.*
  
 <p align="center">
  <img src="https://github.com/GregMurray30/recommendation_engines/blob/master/visualizations/mean_v_wrdv_2.png" title="Mean Rating X vs. WRDV: Divergent and Identical Ratings">
 </p>
 
 **Figure 3c:** *The **WRDV** on the y axis plotted against the mean rating of item x on the x axis with params α=1 and γ=.25, holding the standard deviation of the item constant. The blue curve models the effect of an item's mean rating on wrdv when user u and user v have completely divergent ratings (5 vs 1). The two highest points on the wrdv axis (least likely to be similar) occur when one user agrees with the average rating and the other does not. Conversely, the black curve reflects the effect on wrdv when user u and user v have completely identical ratings (5 vs 5). In that scenario, the highest point occurs when the two users' ratings agree with average rating of the item. **The belief is that liking wildly popular or unpopular items is not particularly revealing of profound commonalities in taste**.*




The intuition behind weighting each rating difference as such is to lend varying importance to items/users depending on, in the case of items, the degree to which there is a consensus of opinion for that item, and what that consensus is. In the case of users, emphasis varies according divergence from their average rating and as a function of their consistency (consistently sympathetic reviewers rating an item poorly is potentially indicative of a very poor item).
 
Examining consistency, in figure 3a above, a user pair with a rating difference equal to 0 (red curve), on an item with standard deviation equal to 1 will have a wrdv of 1. In comparison, in order for a user pair with a rating difference of 3 on an item (green curve), divergent opinions, to obtain the same wrdv, the standard deviation must be 4 times higher with σ<sub>a</sub> equal to 4, where essentially no one agrees<sup>[3](#3)</sup>.

Because the range of the weighted rating difference values is continuous, the model assumes a Gaussian random variable to model the similarity of any two nodes. 

<p align="center">
  <img src="https://github.com/GregMurray30/recommendation_engines/blob/master/visualizations/gauss_dists.png" title="Gauss Dists">
 </p>
 
**Figure 4:** *Examples of wrdv (x axis) Gaussian probability density functions for three different user pairs of varying similarity and variance. If the threshold paramater θ were set at 1, then each user pair's edge distance would be the area under that pair's curve to the **left** of the pink dashed line. Therefore, in this example, user pair A-B has the highest probability of similarity, followed by user pair A-D, then user pair A-C with the lowest similarity probability.*

#### CROSS EDGES
The cross edges in the Gaussian Model use a different scaling system than the Pearson model. A non-linear transformation is applied to the raw ratings between a user node and movie node. Each rating from 0.5 to 5 is assigned a value from 0 to 1, with a rating of 5 assigned a value of 1 and the other ratings assigned weights at uneven intervals.

#### ZERO VARIANCE PROBLEM
One (major) shortcoming of the probabilistic approach to edge weights is that since the Gaussian probability density is ![alt text](https://wikimedia.org/api/rest_v1/media/math/render/svg/4abaca87a10ecfa77b5a205056523706fe6c9c3f "Title"), it is undefined for samples with a variance (**σ<sup>2</sup>**) of zero. Intuitively, the cumulative distribution function (CDF) for a distribution with zero variance is defined as ![alt text](https://wikimedia.org/api/rest_v1/media/math/render/svg/90400cbbc8895d9f3c9a62d7502ed0f077c6ee3b).
However, because many of the instances with zero variance are clearly more a result of small sample size than two users' unwavering similarity, this CDF is not a practical solution to the zero variance problem (which is really a sample size problem). 

It should be noted that the sample size referenced here is the number of items two users have rated, not the global data set size. This means that the problem will almost certainly not be resolved with additional observations in the global data set as there will always be many pairs of users who overlap in only a few items. Consequently, the zero variance problem is actually a property of the subject domain with a power-law or [positively-skewed normal network distribution](#PEARSON_NETWORK_MODEL), not a transient issue of small sample size in the common statisical sense. A long-term solution to circumvent the problem is needed.

To address the zero variance issue then, when the mean difference is less than the threshold parameter **θ** (and the variance is zero, obviously), distance is calculated using a sigmoid function, *δ(n)=e<sup>n</sup>/(1000+e<sup>n</sup>)* [<sup>5</sup>](#5), where **n** is the sample size. In the case where the mean difference is greater than the threshold parameter and the variance is zero, the edge is set equal to zero, effectively removing the two nodes' connection from the network. Formally, distance in this network is calculated where
  
  >**δ<sub>uv</sub>(N(μ<sub>uv</sub>, σ<sup>2</sup><sub>uv</sub>); θ)=Pr[N(μ<sub>uv</sub>, σ<sup>2</sup><sub>uv</sub>)<θ]**, when **σ<sup>2</sup><sub>uv</sub>>0** and **μ<sub>uv</sub><=θ**;
  
  >**δ<sub>uv</sub>(N(μ<sub>uv</sub>, σ<sup>2</sup><sub>uv</sub>); θ)=e<sup>n<sub>uv</uv></sup>/(1000+e<sup>n</sup>)**, when **σ<sup>2</sup><sub>uv</sub>=0** and **μ<sub>uv</sub><=θ**, where n is the sample size of **E<sub>uv</sub>**;
  
  >**δ<sub>uv</sub>(N(μ<sub>uv</sub>, σ<sub>uv</sub>); θ)= 0**, otherwise,

where δ<sub>uv</sub> is the edge distance for node pair u-v.
  
#### MODEL ADVANTAGES & DISADVANTAGES

One of the advantages of using a dual node-type network model is that the user's item
ratings, her similarity to other users, and other items similarity to items she rated, are not considered in any arbitrary order, but rather assessed simultaneously[<sup>6</sup>](#6). In addition, each node type's edge distances may be weighted according to one's beliefs about the impact that particular type.

## TESTING THE MODELS
In order to test the predictive ability of the two models the "leave-one-out" (LVOO) cross validation technique is used. In this way the network can be left virtually unchanged whilst composing the training data sets.

## FUTURE ITERATIONS & MODEL IMPROVEMENTS
There are a few ways in which the models might be improved. First, adding a time component to the models. Second, allowing for more information on the item or user than simply its volatility to weight the rating differences.

There is currently no dimension of time incorporated in the model, and it is fairly certain that our tastes, and therefore the distributions that model the similarity between two users, evolve over time. The extent to which these time series of ratings display a Markovian property (that the best approximation of a probability for a time series is based on the most recent observation) could determine the weightings for each rating observation.
 
Rather than just using the standard deviation to weight each node pair's rating differences, the mean value may also be used to some effect in that weighting equation. But difficulties quickly arise in implementing this information without blowing the whole thing into an oblivion of spurious relationships and non-sensical outcomes. The difficulties in assessing the meaning of the various outcomes and modelling them mathematically are deeper and more complex than they at first seem.

## *NOTES*

>###### 1
> *Outside of the context of a single node path traversal the graph is non-directed and cyclic. It is only when an individual path is being assessed that the graph becomes directed, and acylic as no cycles are allowed and a node path may not "double back" on itself.*

 >###### 2
 >*Adding one to the numerator of the wrdv equation ensures there is no zero outcome when the ratings are identical. The resultant wrdv curve would simply be the x axis - a wrdv of zero regardless of the standard deviation of the item or user.*
 
 >###### 3
 >*Defined thus, a node pair with a rating-difference of 4 can never have a weighted rating-difference value less than 1.25 since the standard deviation for rating differences can never be greater than 4 ((1+4)/4)=1.25)*
 
 >###### 5
 >*The constant 1 in the logistic function is replaced with 1000 in order to achieve the desired scaling of the resulting quantity*
 
 >###### 6
>*In this iteration of the scalar model the distances in the user network, item network, and the
 user-item cross network are scaled the same, assigning each network equal impact on the
 final recommendation. These edge weights could easily be scaled to accomodate one's
 beliefs on the importance each network has in determining the right item recommendation.
 For instance if one believed that item similarity was more important than user
 similarity, the edge weights in the item network plane could be scaled down by some
 factor.*
 
 ## *BIBLIOGRAPHY*
 >J. L. Herlocker, J. A. Konstan, et al., An Algorithmic Framework for Performing Collaborative Filtering , Proceedings of the 22nd Annual International ACM SIGIR Conference, ACM Press, 1999, pp. 230–237.
