import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.externals.six import StringIO
from sklearn.tree import export_graphviz
import pydotplus
import pickle
from sklearn.preprocessing import OrdinalEncoder

dataset = pd.read_csv('trainingset.csv')
dataset.head()

y = dataset['label']
X = dataset.drop("label", axis=1)

# convert categorical values to numerical
enc = OrdinalEncoder()
enc.fit(X)
X = enc.transform(X)

# train classifier
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
rf = RandomForestClassifier(n_estimators=10, random_state=0, max_leaf_nodes=12)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test, y_pred))

with open("model_validation.txt", "w") as f:
    f.write("Confusion Matrix:")
    f.write(confusion_matrix(y_test,y_pred))
    f.write(classification_report(y_test,y_pred))

i = 0
for dtree in rf.estimators_:
    dot_data = StringIO()
    export_graphviz(dtree, out_file=dot_data,
                feature_names=dataset.columns.values[:-1],
                filled=True, rounded=True,
                special_characters=True)
    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())

    with open("Tree_{0}.png".format(str(i)), "wb") as png:
        png.write(graph.create_png())

    i += 1

pickle_file = open('model.pkl', "w")
pickle.dump(rf, pickle_file)
