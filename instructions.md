# recommendation_engine BETA VERSION
>### Movie recommendation engine using Apache Spark
The data sample [files](#1) are a comma separated value file in the format *[user_id], [movie_id], [rating], [rating_date]*. 

Adjust the file path to the data csv file in either USER_MOVIE_NETWORK.py or USER_MOVIE_NETWORK_gaussian.py and execute the code in a PySpark instance. Then, in the same PySpark instance, execute the code from BellmanFord_PySpark.py. For an explanation on the difference between [USER_MOVIE_NETWORK.py](https://github.com/GregMurray30/recommendation_engines/blob/master/USER_MOVIE_NETWORK.py) and [USER_MOVIE_NETWORK_gaussian.py](https://github.com/GregMurray30/recommendation_engines/blob/master/USER_MOVIE_NETWORK_gaussian.py), see [model_conceptual_framework.md](https://github.com/GregMurray30/recommendation_engines/blob/master/model_conceptual_framework.md).

For instruction on installing PySpark on your machine see: https://github.com/mahmoudparsian/big-data-mapreduce-course/blob/master/spark/macbook_and_linux/download_and_install_spark_on_macbook_and_linux.md)

This algorithm is very greedy so even medium sized datasets will take too long to converge on a normal CPU. For anything larger than a few hundred nodes a GPU or server cluster is required (the number of data points in the resultant data
structure is exponentially larger than the number of nodes).

#### IMPORTANT
With the exception of BellmanFord_Python_only.py, the .py files are **NOT** meant for execution in a regular Python environment as they utilize PySpark - an Apache Spark MapReduce framework for Python. The files are meant to be executed via the command terminal in a PySpark instance . Copy and paste the text directly into the terminal, then execute Graph(\<desired user id\>, \<n top movie recommendations\>) for the desired user and n top movie recommendations.
  
  
