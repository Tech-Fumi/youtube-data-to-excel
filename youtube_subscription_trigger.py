
import os
import json
import requests
import base64
import hashlib
from google.cloud import pubsub_v1
from flask import Request, jsonify
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build


# .envファイルから環境変数をロード
load_dotenv()

# 環境変数から値を取得
CHANNEL_ID = os.getenv("CHANNEL_ID")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")
OBS_WS_URL = os.getenv("OBS_WS_URL")
OBS_WS_PASSWORD = os.getenv("OBS_WS_PASSWORD")



def generate_auth_response(password, salt, challenge):
    """
    パスワード認証用のレスポンスを生成
    """
    pass_salt = base64.b64encode(hashlib.sha256((password + salt).encode()).digest()).decode()
    auth_response = base64.b64encode(hashlib.sha256((pass_salt + challenge).encode()).digest()).decode()
    return auth_response

def get_subscriber_count():
    """
    YouTube Data APIを使って登録者数を取得
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        subscriber_count = int(data['items'][0]['statistics']['subscriberCount'])
        return subscriber_count
    except (requests.RequestException, KeyError, IndexError) as e:
        print("登録者数の取得に失敗しました:", e)
        return None

def publish_to_pubsub(subscriber_count):
    """
    登録者数の変化を Pub/Sub トピックに送信
    """
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = PUBSUB_TOPIC
        message_data = json.dumps({"subscriber_count": subscriber_count}).encode("utf-8")
        future = publisher.publish(topic_path, data=message_data)
        print(f"Published message ID: {future.result()}")
    except Exception as e:
        print("Pub/Sub メッセージの送信に失敗しました:", e)

def trigger_obs_event(subscriber_count):
    """
    OBSで通知を表示
    """
    try:
        import websocket
        ws = websocket.create_connection(OBS_WS_URL)
        # 認証が必要な場合
        hello_message = json.loads(ws.recv())
        auth_required = "authentication" in hello_message["d"]
        if auth_required:
            salt = hello_message["d"]["authentication"]["salt"]
            challenge = hello_message["d"]["authentication"]["challenge"]
            auth_response = generate_auth_response(OBS_WS_PASSWORD, salt, challenge)
            ws.send(json.dumps({
                "op": 1,
                "d": {"rpcVersion": 1, "authentication": auth_response}
            }))
            identify_response = json.loads(ws.recv())
            print("Identifyレスポンス:", identify_response)
        ws.close()
    except Exception as e:
        print("OBS WebSocketでエラーが発生しました:", e)

def main(request: Request):
    """
    Cloud Functionのエントリポイント
    """
    try:
        # 登録者数の取得
        current_subscriber_count = get_subscriber_count()
        if current_subscriber_count is None:
            return "Failed to retrieve subscriber count", 500
        # Pub/Sub メッセージの送信
        publish_to_pubsub(current_subscriber_count)
        # 登録者数が増加している場合、OBSで通知
        # ※ ここでは仮に現在の状態のみで動作させています
        print(f"現在の登録者数: {current_subscriber_count}")
        trigger_obs_event(current_subscriber_count)
        return jsonify({"message": "OK", "current_subscriber_count": current_subscriber_count}), 200
    except Exception as e:
        print("Cloud Function内でエラーが発生しました:", e)
        return jsonify({"error": str(e)}), 500
