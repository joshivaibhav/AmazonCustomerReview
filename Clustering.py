import config
from SqlConnector import SqlConnector
import pandas as pd
import preprocessor as p
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import Birch
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
import itertools
from sklearn import metrics
from wordcloud import WordCloud, STOPWORDS

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

class ClusteringModel:
    __slots__ = "sqlConnector", "data"

    columns_list = ['customer_id', 'product_id', 'marketplace', 'review_body',
                    'helpful_votes', 'total_votes', 'review_date',
                    'review_headline',
                    'product_category', 'verified_purchase', 'star_rating']

    def __init__(self):
        self.sqlConnector = SqlConnector()
        self.generate_data()

    def generate_data(self):
        reviews = self.sqlConnector.getRows(config.db['dbname'],
                                            config.db['table'])
        reviews = pd.DataFrame(reviews, columns=self.columns_list)

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

        # downsample positive reviews to balance the dataset
        positive_reviews = positive_reviews.sample(n=len(negative_reviews))

        positive_reviews['was_helpful'] = 1
        negative_reviews['was_helpful'] = 0
        self.data = positive_reviews.append(negative_reviews)

    def tfidf_vectorizer(self):
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        return vectorizer

    def birch(self):
        headlines = self.data[Columns.REVIEW_HEADLINE]
        vectorizer = self.tfidf_vectorizer()
        headlines_vectorized = vectorizer.fit_transform(headlines.apply(p.preprocess_review))
        scaler = StandardScaler()
        birch = Birch().fit(scaler.fit_transform(headlines_vectorized.toarray()))
        labels = birch.labels_

        clusters = {}

        for index, headline in enumerate(headlines):
            if labels[index] != -1:
                if labels[index] in clusters:
                    clusters[labels[index]] += " " + headline
                else:
                    clusters[labels[index]] = headline
        for cluster in clusters.keys():
            self.generate_wordcloud(cluster, clusters[cluster])

    def generate_wordcloud(self, cluster, text):
        '''
        Citation: https://github.com/amueller/word_cloud
        :param cluster:
        :param text:
        :return:
        '''
        wordcloud = WordCloud(collocations=False).generate(text)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig("wordcloud/" + str(cluster) + ".jpg")

model = ClusteringModel()
model.birch()