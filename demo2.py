import nltk
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googleapiclient.discovery import build
import re
import string

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

# Визуализация результатов с помощью matplotlib
plt.figure(figsize=(8, 6))
plt.bar(['Positive', 'Neutral', 'Negative'], [len(positive), len(neutral), len(negative)], color=['green', 'gray', 'red'])
plt.title('Распределение настроений комментариев')
plt.xlabel('Настроение')
plt.ylabel('Количество комментариев')
plt.show()

# Для использования Streamlit:
import streamlit as st
import pandas as pd

# Преобразуем данные в DataFrame для удобства отображения
df = pd.DataFrame(sentiments)

# Создаем интерактивный дашборд с Streamlit
st.title('Анализ настроений комментариев YouTube')
st.write('Распределение настроений:')
st.bar_chart([len(positive), len(neutral), len(negative)], x=['Positive', 'Neutral', 'Negative'])

st.write('Пример комментариев с их тональностью:')
st.write(df.head())

# Запускаем сервер Streamlit
# Строку ниже необходимо раскомментировать, если хотите запустить Streamlit на локальном сервере:
# st.run()
