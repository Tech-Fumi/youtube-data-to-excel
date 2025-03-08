YouTube Subscription & Video Analytics Automation

概要

このプロジェクトは、YouTubeチャンネルの登録者数を取得し、その変化をGoogle Cloud Pub/Subに送信する機能と、YouTubeの動画情報およびアナリティクスデータを取得し、Excelファイルに保存する機能を提供します。

ファイル構成

1. youtube_subscription_trigger.py

YouTubeの登録者数を取得し、以下の処理を行います。

YouTube Data APIを使用して登録者数を取得

Google Cloud Pub/Subに登録者数を送信

登録者数の変化をOBSに通知

Google Cloud Functionsを想定したエントリーポイントを提供

2. youtube_videos.py

YouTube APIを使用して、指定チャンネルの動画情報とアナリティクスデータを取得し、Excelファイルに保存します。

YouTube Data APIで動画の基本情報（動画ID、タイトル、公開日時）を取得

YouTube Analytics APIで各動画の視聴数、総視聴時間、いいね数、コメント数を取得

データをExcelファイル（youtube_analytics_data.xlsx）に保存

必要な環境変数

.env ファイルを作成し、以下の値を設定してください。

CHANNEL_ID=あなたのチャンネルID
YOUTUBE_API_KEY=YouTube Data APIキー
PUBSUB_TOPIC=Google Cloud Pub/Subのトピック
OBS_WS_URL=OBS WebSocketのURL
OBS_WS_PASSWORD=OBS WebSocketのパスワード

必要なライブラリ

以下のライブラリが必要です。インストールされていない場合は、pip install -r requirements.txt でインストールしてください。

flask
requests
google-cloud-pubsub
dotenv
google-auth-oauthlib
google-auth-httplib2
google-auth google-api-python-client
pandas
openpyxl

実行方法

youtube_subscription_trigger.py の実行

Google Cloud Functionsなどの環境で動作することを想定していますが、ローカルで試す場合は以下のようにFlaskを利用して実行できます。

export FLASK_APP=youtube_subscription_trigger.py
flask run

または、直接スクリプトを実行することも可能です。

python youtube_subscription_trigger.py

youtube_videos.py の実行

YouTubeの動画情報とアナリティクスデータを取得するには、以下のコマンドを実行してください。

python youtube_videos.py

成功すると、youtube_analytics_data.xlsx というExcelファイルが作成されます。

認証について

youtube_videos.py はYouTube Data APIおよびYouTube Analytics APIを使用します。OAuth認証が必要なため、事前に client_secret.json を取得し、スクリプト実行時に認証を完了してください。

認証情報は token.pickle に保存され、次回以降の認証に利用されます。

注意事項

Google Cloud Pub/Subの設定が適切に行われていることを確認してください。

YouTube Data APIとAnalytics APIの使用制限（クォータ）に注意してください。

youtube_videos.py は大量のデータを取得する可能性があるため、リクエスト制限を考慮しながら運用してください。

ライセンス

このプロジェクトはMITライセンスのもとで公開されています。
