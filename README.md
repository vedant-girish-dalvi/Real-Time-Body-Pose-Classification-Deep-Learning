# **Master Thesis Project: Real-Time Body Pose Classification using Deep Learning in Microservices Architecture for Human-Exoskeleton Interaction**

In recent years, industrial exoskeletons have been in demand for executing strenuous
industrial tasks. Despite many advantages, industrial exoskeletons can restrict body
movements, causing issues like adversely affecting dynamic job performance and
causing balance problems, leading to injuries to the user, accidents, or preventing users
from escaping emergencies quickly.
In this project, a solution has been developed to overcome this issue via a real-time bodypose
classification application using deep learning in a microservices architecture. The
proposed application uses a motion capture suit with IMU sensors as a data source and
a back-support exoskeleton that provides sequential data of body joint angles. Data was
collected from multiple participants for a logistic task. After data collection, three deep
learning-based model architectures were trained on this data: LSTM, GRU, and
Transformer. The trained models were deployed in a server in a microservices
architecture-based application for real-time body pose inference. Several experiments
were performed to evaluate the real-time classification performance of trained classifiers.
The experiments demonstrated that the Transformer model gave the most accurate
results in real-time on unseen data. In addition, microservices architecture validated its
advantages over the traditional monolithic architecture in terms of scalability and latency.
Lastly, after conducting the experiments with and without an exoskeleton, a significant
difference in real-time classification accuracy was observed, validating that exoskeletons
affect user mobility.
Although the proposed application gave good results, further research and analysis is
necessary to create a more robust solution.
