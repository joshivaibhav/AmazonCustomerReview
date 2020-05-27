import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS
import pandas as pd


def random_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):

    h = int(260.0 * 45.0 / 255.0)
    s = int(150.0 * 255.0 / 255.0)
    l = int(100.0 * float(random_state.randint(60, 120)) / 255.0)

    return "hsl({}, {}%, {}%)".format(h, s, l)


def gen_wordcloud(data):

    all_reviews = ""
    #count = 50000
    for review in data['Review Body']:
        #if count == 0:
         #   break
        all_reviews = all_reviews + str(review) + ' '
        #count-=1
    all_reviews = all_reviews.replace('<br>','')
    all_reviews = all_reviews.replace('</br>','')
    all_reviews = all_reviews.replace('<br />', '')

    wordcloud = WordCloud(font_path = r'C:\Windows\Fonts\Tahoma.ttf',
                            stopwords = STOPWORDS,
                            background_color = 'white',
                            width = 800,
                            height = 600,
                            color_func = random_color_func
                            ).generate(all_reviews)

    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()

if __name__ == '__main__':

    data = pd.read_csv("amazondata.csv")
    data.dropna(inplace=True)
    data_bad_ratings = data.loc[data['Star Rating'] < 3]
    data_good_ratings = data.loc[data['Star Rating'] >= 3]
    #gen_wordcloud(data_bad_ratings)
    gen_wordcloud(data_good_ratings)