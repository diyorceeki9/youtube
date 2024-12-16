import nltk
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googleapiclient.discovery import build
import re
import string
import pandas as pd
import streamlit as st

# Инициализация API YouTube
api_key = 'AIzaSyChZN6p73x3NgBpDoWFM_ZhIjv_gFXmdSc'  # Замените на свой API ключ
youtube = build('youtube', 'v3', developerKey=api_key)

# Функция для получения комментариев с YouTube
def get_video_comments(video_id, max_results=100):
    comments = []
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=max_results,
        textFormat='plainText'
    )
    response = request.execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        # Если есть следующая страница, получаем её
        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                pageToken=response['nextPageToken'],
                textFormat='plainText'
            )
            response = request.execute()
        else:
            break
    return comments

# Функция предобработки текста
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)  # Убираем ссылки
    text = re.sub(r'\d+', '', text)  # Убираем цифры
    text = text.translate(str.maketrans('', '', string.punctuation))  # Убираем знаки препинания
    return text

# Анализ тональности с использованием VADER
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    return sia.polarity_scores(text)

# ID видео на YouTube
video_id = 'uXfJ2m3Cyag'  # Замените на нужное ID видео

# Получаем комментарии
comments = get_video_comments(video_id)
print(f"Собрано {len(comments)} комментариев")

# Предобрабатываем комментарии
processed_comments = [preprocess_text(comment) for comment in comments]

# Анализируем тональность каждого комментария
sentiments = [analyze_sentiment(comment) for comment in processed_comments]

# Разбиваем на 3 категории: positive, neutral, negative
positive = [s['compound'] for s in sentiments if s['compound'] > 0.1]
neutral = [s['compound'] for s in sentiments if -0.1 <= s['compound'] <= 0.1]
negative = [s['compound'] for s in sentiments if s['compound'] < -0.1]

# Визуализация распределения настроений в Streamlit
sentiment_counts = {'Positive': len(positive), 'Neutral': len(neutral), 'Negative': len(negative)}
df = pd.DataFrame(list(sentiment_counts.items()), columns=['Sentiment', 'Count'])

# Строим график
st.title('Анализ настроений комментариев YouTube')
st.write('Распределение настроений:')

# Отображаем столбчатую диаграмму
st.bar_chart(df.set_index('Sentiment'))

# Пример таблицы с данными
st.write('Таблица с результатами анализа настроений:')
st.write(df)

