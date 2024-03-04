from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import warnings
import jieba
import pathlib



warnings.filterwarnings("ignore")


# jieba slipt chinese words
def chinese_word_cut(mytext):
    return " ".join(jieba.cut(mytext))


# get custom stopwords
def get_custom_stopwords(stop_words_file):
    with open(stop_words_file, encoding="utf-8") as f:
        stopwords = f.read()
    stopwords_list = stopwords.split("\n")
    custom_stopwords_list = [i for i in stopwords_list]
    return custom_stopwords_list


def preprocess_data(data):
    data["comment"] = data["comment"].astype(str)
    data["cut_comment"] = data["comment"].apply(chinese_word_cut)
    return data


# Function to vectorize text
def vectorize_text(data, stopwords):
    vect = CountVectorizer(token_pattern=r"(?u)\b\w+\b", stop_words=stopwords)
    X_vect = vect.fit_transform(data["cut_comment"])
    return vect, X_vect


# Function to train the model
def train_model(X_vect, y):
    smote = SMOTE(random_state=22)
    X_resampled, y_resampled = smote.fit_resample(X_vect, y)
    model = MultinomialNB()
    model.fit(X_resampled, y_resampled)
    return model


# Function to make predictions
def make_predictions(model, vect, data):
    X_vect = vect.transform(data["cut_comment"])
    predictions = model.predict(X_vect)
    return predictions


### Change output into plottly format ###
import plotly.graph_objs as go

import plotly.graph_objs as go

def generate_confusion_matrix(y_true, predictions, title):
    cm = confusion_matrix(y_true, predictions)
    cm_normalized = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    cm_labels = ["Highly Recommended", "Recommended", "Fair", "Poor", "Very Poor"]
    cm_df = pd.DataFrame(data=cm_normalized, columns=cm_labels, index=cm_labels)

    # Create a list to store annotations
    annotations = []
    for i, row in enumerate(cm_labels):
        for j, val in enumerate(cm_labels):
            annotations.append(
                dict(text=str("{:.2f}".format(cm_normalized[i, j])),
                     x=cm_labels[j], y=cm_labels[i],
                     xref='x1', yref='y1',
                     font=dict(color='black' if i != j else 'white'))
            )

    heatmap = go.Heatmap(z=cm_df.values,
                         x=cm_labels,
                         y=cm_labels,
                         colorscale='YlGnBu',
                         zmin=0,
                         zmax=1)

    layout = go.Layout(title=title,
                       xaxis=dict(title='Predicted'),
                       yaxis=dict(title='Actual'),
                       annotations=annotations)

    fig = go.Figure(data=[heatmap], layout=layout)

    return fig




### change ###
# Main process function
def process_and_visualize(df, fname, stop_words_file):
    stopwords = get_custom_stopwords(stop_words_file)
    data = preprocess_data(df)
    y = data["score"]
    vect, X_vect = vectorize_text(data, stopwords)
    model = train_model(X_vect, y)

    predictions = make_predictions(model, vect, data)
    fig = generate_confusion_matrix(
            y, predictions, f"{fname}" + " Sentiment Analysis Confusion Matrix"
        )
    return fig


### Change main part to function ###
def execute_sentiment_analysis():
    # Load datasets
    df_douban = pd.read_excel(pathlib.Path(__file__).parent / "douban_clean_sentiment_analysis.xlsx")
    df_douban["score"] = df_douban["score"].map(
        {"力荐": "1", "推荐": "2", "还行": "3", "较差": "4", "很差": "5"}
    )

    df_rottentomatoes = pd.read_excel(pathlib.Path(__file__).parent / "rottentomatoes_clean_sentiment_analysis.xlsx")
    df_rottentomatoes["score"] = df_rottentomatoes["score"].map(
        {
            5: "1",
            4.5: "1",
            4: "2",
            3.5: "2",
            3: "3",
            2.5: "3",
            2: "4",
            1.5: "4",
            1: "5",
            0.5: "5",
        }
    )

    # Process and visualize
    stop_words_file = pathlib.Path(__file__).parent / "stop_words.txt"
    fig_d = process_and_visualize(df_douban, "Douban", stop_words_file)
    fig_r = process_and_visualize(df_rottentomatoes, "Rottentomatoes", stop_words_file)
    return fig_d, fig_r
