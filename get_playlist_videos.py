# %%

import os
import csv
import configparser
import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv

def save_playlist_videos_to_csv(api_key, playlist_id, playlist_name, csv_filepath):
    """
    指定されたYouTube再生リストの動画情報を取得し、指定されたCSVファイルに追記します。
    重複するビデオIDは追加しません。
    """
    
    try:
        # Step 0: 既存のCSVファイルからビデオIDを読み込む（重複チェックのため）
        existing_video_ids = set()
        try:
            with open(csv_filepath, mode="r", newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader) # ヘッダーをスキップ
                for row in reader:
                    if row: # 空行をチェック
                        # 5列目（ビデオID）のデータを重複チェック用セットに追加
                        existing_video_ids.add(row[4]) 
        except FileNotFoundError:
            print(f"'{csv_filepath}' が見つかりません。新規に作成します。")

        # YouTube APIクライアントをビルド
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key)

        print(f"再生リスト「{playlist_name}」の情報を取得中...")

        # Step 1: playlistItems.listで再生リスト内の全動画IDとタイトルを取得
        video_details = {}
        next_page_token = None

        while True:
            playlist_request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()

            for item in playlist_response.get("items", []):
                if "videoId" in item["snippet"]["resourceId"]:
                    video_id = item["snippet"]["resourceId"]["videoId"]
                    if video_id not in existing_video_ids:
                        video_details[video_id] = {
                            "id": video_id,
                            "title": item["snippet"]["title"],
                            "tags": []
                        }
            
            next_page_token = playlist_response.get("nextPageToken")
            if not next_page_token:
                break
        
        if not video_details:
            print("追加する新しい動画はありませんでした。")
            return

        # Step 2: videos.listで新規動画のタグ情報を一括取得
        new_video_ids = list(video_details.keys())
        for i in range(0, len(new_video_ids), 50):
            chunk_ids = new_video_ids[i:i+50]
            video_request = youtube.videos().list(
                part="snippet",
                id=",".join(chunk_ids)
            )
            video_response = video_request.execute()

            for item in video_response.get("items", []):
                video_id = item["id"]
                if "tags" in item["snippet"]:
                    video_details[video_id]["tags"] = item["snippet"]["tags"]

        # Step 3: 取得した情報をCSVファイルに追記する
        write_header = not os.path.exists(csv_filepath)
        
        with open(csv_filepath, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if write_header:
                # 指定された順番でヘッダーを定義
                header = ["タイトル", "URL", "タグ", "プレイリスト名", "ビデオID", "プレイリストID"]
                writer.writerow(header)

            for video_id, details in video_details.items():
                # 指定された順番で各行のデータを定義
                row = [
                    details["title"],
                    f"https://www.youtube.com/watch?v={video_id}",
                    ", ".join(details["tags"]),
                    playlist_name,
                    video_id,
                    playlist_id
                ]
                writer.writerow(row)
        
        print(f"完了しました。{len(video_details)}件の動画データを '{csv_filepath}' に追加しました。")

    except googleapiclient.errors.HttpError as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
    except IOError as e:
        print(f"ファイル書き込み中にエラーが発生しました: {e}")


if __name__ == "__main__":
    # .envファイルからAPIキーを読み込み
    load_dotenv()
    API_KEY = os.getenv("YOUTUBE_API_KEY")

    # config.iniから設定を読み込み
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    
    try:
        config.read(config_file, encoding='utf-8')
        playlist_id = config.get('YouTube', 'playlist_id')
        playlist_name = config.get('YouTube', 'playlist_name')
        csv_filename = config.get('YouTube', 'csv_filename')
    except (FileNotFoundError, configparser.Error):
        print(f"'{config_file}' が見つからないか、内容が不適切です。デフォルト設定を使用します。")
        playlist_id = "PLOU2XLYxmsIKC8eODk_RjI5gG__v2EX1B"
        playlist_name = "Google Developers Japan"
        csv_filename = "movies_default.csv"

    # 出力用フォルダの設定
    OUTPUT_DIR = "output"
    # フォルダが存在しない場合は作成
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # CSVファイルのフルパスを生成
    csv_filepath = os.path.join(OUTPUT_DIR, csv_filename)

    if not API_KEY:
        print("エラー: .envファイルに 'YOUTUBE_API_KEY' を設定してください。")
    elif not playlist_id:
        print("エラー: プレイリストIDが設定されていません。")
    else:
        save_playlist_videos_to_csv(API_KEY, playlist_id, playlist_name, csv_filepath)

# %%
