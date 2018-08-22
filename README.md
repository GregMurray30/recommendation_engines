# recommendation_engine BETA VERSION
Movie recommendation engine using Apache Spark
Ratings_sample.txt is "::" separated value file in the format [user_id]::[movie_id]::[rating]::[rating_date]. 

For instruction on installing PySpark on your machine see: https://github.com/mahmoudparsian/big-data-mapreduce-course/blob/master/spark/macbook_and_linux/download_and_install_spark_on_macbook_and_linux.md)

This algorithm is very greedy so even medium sized datasets will take too long to run on a normal CPU. A GPU or server cluster is needed.


IMPORTANT: With the exception of BellmanFord_Python_only.py, the .py files are NOT meant for execution in a regular Python environment as they utilize PySpark - an Apache Spark MapReduce framework for Python. The files are meant to be executed via the command terminal in a PySpark instance . Copy and paste the text directly into the terminal, then execute Graph(<desired user id>, <n top movie recommendations>) for the desired user and n top movie recommendations.
  
  
