from googleapiclient.discovery import build
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
# Убедись, что установлены библиотеки: pip install google-api-python-client nltk
import nltk
# nltk.download('all')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')
# Настройки API
api_key = "AIzaSyChZN6p73x3NgBpDoWFM_ZhIjv_gFXmdSc"
youtube = build('youtube', 'v3', developerKey=api_key)
# Функция для получения комментариев
def get_video_comments(video_id, max_results=100):
    comments = []
    next_page_token = None
    while True:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            pageToken=next_page_token,
            textFormat="plainText"
        ).execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        # Проверка на следующую страницу
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return comments
# Функция для предобработки текста
def preprocess_text(text):
    # Удаление ссылок
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Удаление лишних символов
    text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', '', text)
    # Приведение к нижнему регистру
    text = text.lower()
    # Токенизация
    tokens = word_tokenize(text)
    # Удаление стоп-слов
    stop_words = set(stopwords.words('english'))  # Для английского
    tokens = [word for word in tokens if word not in stop_words]
    # Лемматизация
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    # Возвращаем текст после обработки
    return " ".join(tokens)
# Получение комментариев
video_id = "uXfJ2m3Cyag"  # Вставь ID видео
comments = get_video_comments(video_id)
print(f"Собрано {len(comments)} комментариев")

# Предобработка комментариев
processed_comments = [preprocess_text(comment) for comment in comments]

# Вывод первых 5 комментариев до и после обработки
print("\nПервые 5 комментариев ДО обработки:")
for comment in comments[:5]:
    print(comment)

print("\nПервые 5 комментариев ПОСЛЕ обработки:")
for comment in processed_comments[:5]:
    print(comment)
