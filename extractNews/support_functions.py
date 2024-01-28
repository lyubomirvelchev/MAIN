import flair
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

xml_special_char = {
    '&lt;': '<',
    '&amp;': "&",
    '&gt;': '>',
    '&quot;': '\"',
    '&apos;': '\''
}


def flair_prediction(x):
    sentence = flair.data.Sentence(x)
    sia.predict(sentence)
    score = sentence.labels[0]
    if "POSITIVE" in str(score):
        return "pos"
    elif "NEGATIVE" in str(score):
        return "neg"
    else:
        return "neu"


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
