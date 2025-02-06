# Description: This script trains a machine learning model for multi-label 
# classification using a Naive Bayes classifier.

import sys
import warnings
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# Suppress warnings for clarity
if not sys.warnoptions:
    warnings.simplefilter("ignore")

def preprocess_text(data_raw):
    """
    Preprocesses the text data by cleaning and removing stopwords.
    """
    data_raw['Heading'] = (
        data_raw['Heading']
        .str.lower()
        .str.replace(r'[^\w\s]', '', regex=True)
        .str.replace(r'\d+', '', regex=True)
        .str.replace(r'<.*?>', '', regex=True)
    )

    #nltk.download('stopwords')
    stop_words = set(stopwords.words('swedish'))

    def remove_stopwords(sentence):
        return " ".join([word for word in nltk.word_tokenize(sentence) if word not in stop_words])

    data_raw['Heading'] = data_raw['Heading'].apply(remove_stopwords)

    stemmer = SnowballStemmer("swedish")

    def stemming(sentence):
        return " ".join([stemmer.stem(word) for word in sentence.split()])

    # Uncomment if stemming is needed
    # data_raw['Heading'] = data_raw['Heading'].apply(stemming)

    return data_raw

def train_model(data_path):
    """
    Trains the machine learning model and returns the best pipeline and vectorizer.
    """
    print("Loading data...")
    data_raw = pd.read_csv(data_path)

    print("Shuffling data...")
    data_raw = data_raw.sample(frac=1)

    print("Preprocessing data...")
    categories = list(data_raw.columns.values)[2:]  # Excluding 'Id' and 'Heading'
    data_raw = preprocess_text(data_raw)

    print("Splitting data into train and test sets...")
    train, test = train_test_split(data_raw, random_state=42, test_size=0.30, shuffle=True)
    train_text, test_text = train['Heading'], test['Heading']

    print("Vectorizing text data...")
    vectorizer = TfidfVectorizer(strip_accents='unicode', analyzer='word', ngram_range=(1, 3), norm='l2')
    vectorizer.fit(train_text)

    x_train = vectorizer.transform(train_text)
    y_train = train.drop(labels=['Id', 'Heading'], axis=1)

    print("Setting up the ML pipeline...")
    MultinomialNB_pipeline = Pipeline([
        ('clf', OneVsRestClassifier(MultinomialNB())),
    ])

    print("Performing hyperparameter tuning...")
    param_grid = {
        'clf__estimator__alpha': [0.20, 0.21, 0.22],
        'clf__estimator__fit_prior': [True, False]
    }

    grid = GridSearchCV(MultinomialNB_pipeline, param_grid, cv=5, scoring='accuracy')
    grid.fit(x_train, y_train)

    print("Best score: ", grid.best_score_)
    print("Best params: ", grid.best_params_)
    print("Best estimator: ", grid.best_estimator_)

    best_clf_pipeline = grid.best_estimator_
    best_clf_pipeline.fit(x_train, y_train)

    return vectorizer, best_clf_pipeline, categories, test_text, test

def evaluate_model(vectorizer, best_clf_pipeline, test_text, test):
    """
    Evaluates the trained model on test data.
    """
    print("Transforming test data...")
    x_test = vectorizer.transform(test_text)
    y_test = test.drop(labels=['Id', 'Heading'], axis=1)

    print("Predicting test data...")
    y_pred_proba = best_clf_pipeline.predict_proba(x_test)
    threshold = 0.3  # Adjust threshold if needed
    y_pred = (y_pred_proba >= threshold).astype(int)

    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)

def main():
    """
    Main function to orchestrate model training and evaluation.
    """
    print('-----Starting MLModelMLC_3.py-----')
    global categories, vectorizer, best_clf_pipeline  # Make these global for other scripts to import
    data_path = "Book1.csv"  # Adjust path to your data file

    print("Starting model training...")
    vectorizer, best_clf_pipeline, categories, test_text, test = train_model(data_path)

    print("Evaluating model...")
    evaluate_model(vectorizer, best_clf_pipeline, test_text, test)

    print("Model training and evaluation completed.")
if __name__ == "__main__":
    main()