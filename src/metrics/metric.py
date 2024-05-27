import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report

labels = ["standing", "lifting", "carrying", "keeping", "unnatural"]

def metric(y_test, classes):
    cm = confusion_matrix(y_test, classes)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)

    disp.plot(cmap=plt.cm.Blues)
    plt.show()

    print(classification_report(y_test, classes))