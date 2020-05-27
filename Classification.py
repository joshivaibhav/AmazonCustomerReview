import config
from SqlConnector import SqlConnector
import pandas as pd
import preprocessor
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC
import matplotlib.pyplot as plt
import numpy as np
import itertools

class Columns:
    CUSTOMER_ID = "customer_id"
    PRODUCT_ID = "product_id"
    MARKETPLACE = "marketplace"
    REVIEW_BODY = "review_body"
    REVIEW_DATE = "review_date"
    HELPFUL_VOTES = "helpful_votes"
    TOTAL_VOTES = "total_votes"
    REVIEW_HEADLINE = "review_headline"
    PRODUCT_CATEGORY = "product_category"
    VERIFIED_PURCHASE = "verified_purchase"
    STAR_RATING = "star_rating"

class ClassificationModel:
    __slots__ = "sqlConnector", "data"

    columns_list = ['customer_id', 'product_id', 'marketplace', 'review_body',
                    'helpful_votes', 'total_votes', 'review_date',
                    'review_headline',
                    'product_category', 'verified_purchase', 'star_rating']
    
    def __init__(self):
        self.sqlConnector = SqlConnector()
        self.generate_data()

    def generate_data(self):
        reviews = self.sqlConnector.getRows(config.db['dbname'], config.db['table'])
        reviews = pd.DataFrame(reviews, columns = self.columns_list)

        # Remove reviews with zero votes
        reviews_with_votes = reviews.loc[reviews['total_votes'] > 0]

        # Of all the total votes majority have voted helpful
        positive_reviews = reviews_with_votes.loc[
            reviews[Columns.HELPFUL_VOTES] / reviews[
                Columns.TOTAL_VOTES] >= 0.5]

        # Of all the total votes majority have not voted helpful
        negative_reviews = reviews_with_votes.loc[
            reviews[Columns.HELPFUL_VOTES] / reviews[
                Columns.TOTAL_VOTES] < 0.5]

        # upsample negative reviews to balance the dataset
        negative_reviews = negative_reviews.sample(n = len(positive_reviews), replace = True)

        positive_reviews['was_helpful'] = 1
        negative_reviews['was_helpful'] = 0
        self.data = positive_reviews.append(negative_reviews)

    def create_train_test_data(self):
        return train_test_split(self.data[Columns.REVIEW_BODY],
                                self.data['was_helpful'],
                                test_size=0.2,
                                random_state=42)

    def classify(self):
        train_data, test_data, train_labels, test_labels = self.create_train_test_data()

        vectorizer = CountVectorizer(analyzer=preprocessor.preprocess_review).fit(train_data)
        train_data = vectorizer.transform(train_data)

        svc = SVC(random_state=42)
        svc.fit(train_data, train_labels)
        predictions = svc.predict(vectorizer.transform(test_data))

        cm = confusion_matrix(test_labels, predictions)

classifier = ClassificationModel()
classifier.classify()