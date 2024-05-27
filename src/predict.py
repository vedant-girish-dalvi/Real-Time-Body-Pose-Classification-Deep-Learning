#predicting on test datset
import numpy as np
from keras.models import load_model
from sklearn.metrics import accuracy_score

def predict(model, X_test):
    # model = load_model(model_filepath)
    print(type(X_test)) #reshape[1,:,:]
    # print(X_test.shape)
    classify_x=model.predict(X_test) 
    # print(classify_x)
    classes_x=np.argmax(classify_x,axis=1)
    y_test= np.argmax(y_test,axis=1)
    print(classes_x)
    accuracy=accuracy_score(y_test, classes_x)
    accuracy