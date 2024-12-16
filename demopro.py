import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import nltk
import re

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
# YouTube API setup
API_KEY = "AIzaSyChZN6p73x3NgBpDoWFM_ZhIjv_gFXmdSc"
youtube = build("youtube", "v3", developerKey=API_KEY)

# Text preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return ' '.join(tokens)

# Sentiment analysis function
def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return 'Позитивные комменты'
    elif analysis.sentiment.polarity < -0.1:
        return 'Негативные комменты'
    else:
        return 'Нейтральные комменты'

# Fetch YouTube comments
def fetch_comments(video_id):
    comments = []
    likes = []
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        ).execute()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(comment["textOriginal"])
            likes.append(comment.get("likeCount", 0))

    except Exception as e:
        st.error(f"Error fetching comments for video {video_id}: {e}")

    return pd.DataFrame({"Comment": comments, "Likes": likes})

# Streamlit app
st.title("Анализ настроений комментариев YouTube")

st.sidebar.header("Настройки")
video_ids = st.sidebar.text_input("Введите ID видео через запятую")

if video_ids:
    video_ids = [vid.strip() for vid in video_ids.split(",")]
    all_comments = pd.DataFrame()

    for video_id in video_ids:
        st.subheader(f"Видео: {video_id}")

        # Fetch comments
        comments_df = fetch_comments(video_id)
        if comments_df.empty:
            st.write("Не удалось загрузить комментарии для этого видео.")
            continue

        # Preprocess and analyze comments
        comments_df["Cleaned_Comment"] = comments_df["Comment"].apply(preprocess_text)
        comments_df["Sentiment"] = comments_df["Cleaned_Comment"].apply(analyze_sentiment)

        # Display sentiment distribution
        sentiment_counts = comments_df["Sentiment"].value_counts()
        st.bar_chart(sentiment_counts)

        # Show top comments by likes
        st.write("**Топ-5 комментариев по лайкам:**")
        st.write(comments_df.nlargest(5, "Likes")[["Comment", "Likes"]])

        # Append to all_comments
        all_comments = pd.concat([all_comments, comments_df], ignore_index=True)

    # Overall statistics
    st.header("Общая статистика")
    overall_sentiments = all_comments["Sentiment"].value_counts()
    st.bar_chart(overall_sentiments)

    st.write("**Таблица с результатами:**")
    st.dataframe(all_comments)
