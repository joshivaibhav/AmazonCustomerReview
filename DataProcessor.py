import pandas as pd
import gzip
import json
import ast
import json
from SqlConnector import SqlConnector
import mysql.connector
from mysql.connector import errorcode
import math
from datetime import datetime
from dateutil.parser import parse
import numpy as np
import dataset
import config
from sklearn.preprocessing import MultiLabelBinarizer


class DataProcessor:
    __slots__ = "sqlConnector", "dbName", "table", "stanfordDataset", "amazonDataset"

    mandatory = ['customer_id', 'product_id', 'review_body', 'review_date',
                 'helpful_votes', 'review_date', 'review_headline']
    optional = ['product_category', 'image', 'star_rating']

    maxChunksCount = 60

    def __init__(self):
        self.dbName = 'amazon'
        self.table = 'reviews'
        self.sqlConnector = SqlConnector()
        # Create amazon database and review table
        self.sqlConnector.runStatements('sql_statements.sql')
        self.stanfordDataset = StanfordDataset('../reviews_Books_5.json.gz', '../Books.csv')
        self.amazonDataset = AmazonDataset('../amazon_reviews_us_Books_v1_00.tsv')

    def parseAndInsertData(self):
        stanfordReviews = self.stanfordDataset.getReviews()
        self.insertReviews(stanfordReviews, self.stanfordDataset.stanfordColumns)
        stanfordReviews = None
        amazonReviews = self.amazonDataset.getReviews()
        self.insertReviews(amazonReviews, self.amazonDataset.amazonColumns)
        amazonReviews = None

    def insertReviews(self, reriews, columns):
        try:
            for index, review in reviews.iterrows():
                if not self.sqlConnector.rowExists(self.dbName,
                                                     self.table,
                                                        ['customer_id',
                                                         'product_id'],
                                                        [review['customer_id'],
                                                         review['product_id']]):
                    self.sqlConnector.insertValues(self.dbName, self.table, columns, review)
            self.sqlConnector.dbConnection.commit()
        except mysql.connector.Error as err:
            raise Exception(err)


class AmazonDataset:
    """
    source: https://s3.amazonaws.com/amazon-reviews-pds/tsv/index.txt
    """
    __slots__ = "datasetPath"

    amazonColumns = ['customer_id', 'product_id', 'review_body', 'review_date',
                     'helpful_votes', 'review_headline', 'total_votes', 'marketplace',
                     'product_category', 'verified_purchase', 'star_rating']

    def __init__(self, datasetPath):
        self.datasetPath = datasetPath

    def getReviews(self):
        reviews = pd.DataFrame(columns = self.amazonColumns)
        try:
            for chunked_df in pd.read_csv(self.datasetPath, chunksize=1000, sep="\t", error_bad_lines = False):
                chunked_df['verified_purchase'] = chunked_df['verified_purchase'].apply(self.convertVerifiedToBoolean)
                chunked_df = chunked_df[self.amazonColumns]
                reviews = pd.concat([chunked_df, reviews], axis=0)
                if len(reviews) >= 60000:
                    break
            reviews = reviews.dropna()
            reviews['review_headline_len'] = reviews['review_headline'].apply(len)
            reviews = reviews.loc[reviews['review_headline_len'] < 10000]
            reviews = reviews[self.amazonColumns]
        except Exception as err:
            raise err
        return reviews

    def convertVerifiedToBoolean(self, verifiedPurchase):
        if verifiedPurchase == 'Y':
            return 1
        else:
            return 0


class StanfordDataset:
    """
    source: https://nijianmo.github.io/amazon/index.html
    """

    __slots__ = "datasetPath", "ratings", "ratingsFilePath"

    stanfordColumns = ['customer_id', 'product_id', 'review_body', 'review_date',
                        'helpful_votes', 'review_headline', 'total_votes', 'star_rating']

    def __init__(self, datasetPath, ratingsFilePath):
        self.datasetPath = datasetPath
        self.ratingsFilePath = ratingsFilePath

    def parse(self):
        """
        refer:https://nijianmo.github.io/amazon/index.html
        :return:
        """
        g = gzip.open(self.datasetPath, 'rb')
        for l in g:
            yield json.loads(l)

    def getDataframe(self):
        """
        refer:https://nijianmo.github.io/amazon/index.html
        :return:
        """
        rowNo = 0
        df = {}
        maxRows = 120000
        json = self.parse()
        for row in json:
            row['helpful_votes'] = row['helpful'][0]
            row['total_votes'] = row['helpful'][1]
            df[rowNo] = row
            rowNo += 1
            if rowNo >= maxRows:
                break
        reviews = pd.DataFrame.from_dict(df, orient='index')
        reviews = reviews[
            ['reviewerID', 'asin', 'reviewText', 'helpful_votes', 'total_votes',
             'reviewTime', 'summary']]
        reviews.columns = ['customer_id', 'product_id', 'review_body',
                      'helpful_votes',
                      'total_votes', 'review_date', 'review_headline']
        self.ratings = pd.read_csv(self.ratingsFilePath, names=['asin', 'reviewerID', 'star_rating'])
        reviews = pd.merge(reviews, self.ratings, left_on=['product_id', 'customer_id'],right_on=['asin', 'reviewerID'])
        return reviews

    def getReviews(self):
        df = self.getDataframe()
        df['review_date'] = df['review_date'].apply(self.convertToYYYYMMDD)
        df = df.dropna()
        return df

    def convertToYYYYMMDD(self, date):
        #convert date in "dd mm, yyyy" format to "yyyy-mm-dd"
        return datetime.strptime(date, '%m %d, %Y').strftime('%Y-%m-%d')


dp = DataProcessor()
dp.createProductsPerUser()
