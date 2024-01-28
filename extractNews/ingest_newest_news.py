import boto3, multiprocessing
from datetime import datetime, timezone
import flair
import threading
import spacy
from time import sleep
import json
from kafka import KafkaProducer
import yake, summa
from collections import Counter
from string import punctuation
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from keybert import KeyBERT

kw_model = KeyBERT(model='all-mpnet-base-v2')
nlp = spacy.load("en_core_web_lg")
kw_extractor = yake.KeywordExtractor(top=10, stopwords=None)
flair_model = flair.models.TextClassifier.load('en-sentiment')

vader_model = SentimentIntensityAnalyzer()
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk_model = SentimentIntensityAnalyzer()
NEWS_DATA = multiprocessing.Queue()
NEWS_DATA_LOCK = threading.Lock()
FLAIR_LOCK = threading.Lock()

xml_special_char = {
    '&lt;': '<',
    '&amp;': "&",
    '&gt;': '>',
    '&quot;': '\"',
    '&apos;': '\''
}


def flair_prediction(x):
    try:
        sentence = flair.data.Sentence(x)
        FLAIR_LOCK.acquire()
        flair_model.predict(sentence)
        FLAIR_LOCK.release()
        score = sentence.labels[0]
        if "POSITIVE" in str(score):
            return "pos", score.score
        elif "NEGATIVE" in str(score):
            return "neg", score.score
        else:
            return "neu", score.score
    except IndexError:
        return 2, 2


def vader_prediction(x):
    sentiment_dict = vader_model.polarity_scores(x)
    compound_sentiment = sentiment_dict['compound']
    if compound_sentiment >= 0.05:
        return 'pos', compound_sentiment
    elif compound_sentiment <= - 0.05:
        return 'neg', compound_sentiment
    else:
        return 'neu', compound_sentiment


def nltk_prediction(x):
    sentiment_dict = nltk_model.polarity_scores(x)
    compound_sentiment = sentiment_dict['compound']
    if compound_sentiment >= 0.05:
        return 'pos', compound_sentiment
    elif compound_sentiment <= - 0.05:
        return 'neg', compound_sentiment
    else:
        return 'neu', compound_sentiment


def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']
    doc = nlp(text.lower())
    for token in doc:
        if (token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if (token.pos_ in pos_tag):
            result.append(token.text)

    return result


def remove_unnecesary_data(strr):
    keep_char = True
    remove_word = ''
    substrings_to_be_removed = []
    for letter in strr:
        if letter == '<':
            keep_char = False
        elif letter == '>':
            keep_char = True
            remove_word += letter
            substrings_to_be_removed.append(remove_word)
            remove_word = ''
        if not keep_char:
            remove_word += letter
    for word in substrings_to_be_removed:
        strr = strr.replace(word, '')
    for special_char, actual_char in xml_special_char.items():
        strr = strr.replace(special_char, actual_char)
    return strr


def get_sentiment(xml_text, dt):
    title = xml_text.split('<title>')[1].split('</title>')[0]
    body = remove_unnecesary_data(xml_text.split('<body.content>')[1].split('</body.content>')[0]).replace('\n', '')
    if body != '':
        # flair_pred, flair_score = flair_prediction(body)
        # vader_pred, vader_score = vader_prediction(body)
        # nltk_pred, nltk_score = nltk_prediction(body)
        keywords = kw_model.extract_keywords(body, keyphrase_ngram_range=(1, 1), stop_words='english',
                                             highlight=False, top_n=10)
        keywords_list = list(dict(keywords).keys())
        # data = {'dt': str(dt),
                # "flair_pred": flair_pred,
                # 'flair_score': flair_score,
                # "vader_pred": vader_pred,
                # 'vader_score': vader_score,
                # 'nltk_pred': nltk_pred,
                # 'nltk_score': nltk_score,
                # 'keywords_suma': [x[0] for x in summa.keywords.keywords(body, scores=True)[:10]],
                # 'keybert_keywords': keywords_list,
                # 'yake_keywords': [x[0] for x in kw_extractor.extract_keywords(body)[:10]],
                # 'title': title,
                # 'news': body}
        data = {
            "xml": xml_text
        }
        NEWS_DATA.put(data)


def extract_news():

    topic_name = 'hello_world'
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    current_dt = datetime.now(timezone.utc)
    prefix = f'{current_dt.year}{current_dt.month}{current_dt.day}'
    current_dt_buffer = current_dt
    bucket_name = 'chatterquant-moodys'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    counter = 0
    while True:
        for file in bucket.objects.filter(Prefix=prefix):
            while not NEWS_DATA.empty():
                data = NEWS_DATA.get()
                print(f'{counter}:', data, ',')
                producer.send(topic_name, value=data)
                counter += 1
                if counter == 100:
                    return None
            dt = file.last_modified.replace(tzinfo=timezone.utc)
            if dt > current_dt:
                body = file.get()['Body'].read().decode()
                thread = threading.Thread(target=get_sentiment, args=(body, dt,))
                thread.start()
                current_dt_buffer = dt if dt > current_dt_buffer else current_dt_buffer
        current_dt = current_dt_buffer


extract_news()
