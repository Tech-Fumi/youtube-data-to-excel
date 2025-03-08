
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd



# スコープの設定
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly'
]

# 認証の関数
def authenticate():
    credentials = load_credentials()  # トークンを読み込み

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing expired credentials...")
            credentials.refresh(Request())
        else:
            print("No valid credentials found. Starting authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            credentials = flow.run_local_server(port=0)
            save_credentials(credentials)  # 認証後にトークンを保存

    return credentials

# トークン保存・読み込みのユーティリティ
def save_credentials(credentials, filename="token.pickle"):
    with open(filename, "wb") as token_file:
        pickle.dump(credentials, token_file)

def load_credentials(filename="token.pickle"):
    try:
        with open(filename, "rb") as token_file:
            return pickle.load(token_file)
    except FileNotFoundError:
        return None





# YouTube Data APIで動画の基本情報を取得
def get_video_data(youtube):
    videos = []
    next_page_token = None
    while True:
        request = youtube.search().list(
            part='id,snippet',
            channelId='UCdMMQ-rcheXvtKWsuGRP9tg',  # あなたのチャンネルID
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response['items']:
            if item['id']['kind'] == 'youtube#video':
                videos.append({
                    'videoId': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'publishedAt': item['snippet']['publishedAt']
                })
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return videos

# YouTube Analytics APIで詳細データを取得
def get_analytics_data(youtube_analytics, video_id):
    request = youtube_analytics.reports().query(
        ids='channel==MINE',
        startDate='2024-01-01',  # 取得するデータの開始日
        endDate='2024-11-10',    # 終了日
        filters=f'video=={video_id}',
        metrics='views,estimatedMinutesWatched,likes,comments',
        dimensions='day',
        sort='day'
    
    )
    response = request.execute()
    return response.get('rows', [])





def main():
    # 認証と初期化
    credentials = authenticate()
    youtube = build('youtube', 'v3', credentials=credentials)
    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=credentials)

    # 動画データ取得
    video_data = get_video_data(youtube)

    # 各動画のアナリティクスデータ取得
    all_data = []
    metrics_list = ['views', 'estimatedMinutesWatched', 'likes', 'comments']
    for video in video_data:
        analytics_data = get_analytics_data(youtube_analytics, video['videoId'])
        for row in analytics_data:
            # 動的にデータをマッピング
            row_data = dict(zip(metrics_list, row))
            print(f"Row mapped: {row_data}")  # デバッグ用

            all_data.append({
                'videoId': video['videoId'],
                'title': video['title'],
                'publishedAt': video['publishedAt'],
                'views': row_data.get('views', 0),
                'estimatedMinutesWatched': row_data.get('estimatedMinutesWatched', 0),
                'likes': row_data.get('likes', 0),
                'comments': row_data.get('comments', 0),
            })

    # Excelに保存
    df = pd.DataFrame(all_data)
    excel_file = 'youtube_analytics_data.xlsx'
    df.to_excel(excel_file, index=False)
    print(f'Data saved to {excel_file}')

if __name__ == '__main__':
    main()


