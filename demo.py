from googleapiclient.discovery import build

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

# Пример использования
video_id = "uXfJ2m3Cyag"
comments = get_video_comments(video_id)
print(f"Собрано {len(comments)} комментариев")
for comment in comments[:5]:  # Покажем первые 5 комментариев
    print(comment)
