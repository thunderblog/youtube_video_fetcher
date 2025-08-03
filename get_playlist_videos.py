# %%

import os
import csv
import configparser
from typing import Dict, List, Set, Optional, Any

import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv


def load_settings(config_file: str = 'config.ini') -> Dict[str, Optional[str]]:
    """設定ファイル(.env, config.ini)を読み込む"""
    load_dotenv()
    api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")

    config = configparser.ConfigParser()
    try:
        config.read(config_file, encoding='utf-8')
        playlist_id: Optional[str] = config.get('YouTube', 'playlist_id')
        playlist_name: Optional[str] = config.get('YouTube', 'playlist_name')
        csv_filename: Optional[str] = config.get('YouTube', 'csv_filename')
    except (FileNotFoundError, configparser.Error):
        print(f"'{config_file}' が見つからないか不適切です。デフォルト設定を使用します。")
        playlist_id = "PLOU2XLYxmsIKC8eODk_RjI5gG__v2EX1B"
        playlist_name = "Google Developers Japan"
        csv_filename = "movies_default.csv"
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    csv_filepath = os.path.join(output_dir, csv_filename) if csv_filename else None

    return {
        "api_key": api_key,
        "playlist_id": playlist_id,
        "playlist_name": playlist_name,
        "csv_filepath": csv_filepath
    }


def get_existing_video_ids(filepath: str) -> Set[str]:
    """CSVファイルから既存のビデオIDをセットとして取得する"""
    if not os.path.exists(filepath):
        return set()
    
    with open(filepath, mode="r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return set() # 空のファイルの場合
        return {row[4] for row in reader if row} # 5列目(ビデオID)


def fetch_playlist_videos(youtube: Any, playlist_id: str) -> List[Dict]:
    """再生リストから全ての動画情報を取得する"""
    video_items: List[Dict] = []
    next_page_token: Optional[str] = None
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response: Dict = request.execute()
        video_items.extend(response.get("items", []))
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return video_items


def fetch_videos_tags(youtube: Any, video_ids: List[str]) -> Dict[str, List[str]]:
    """複数の動画IDからタグ情報を取得する"""
    tags_map: Dict[str, List[str]] = {}
    for i in range(0, len(video_ids), 50):
        chunk_ids: List[str] = video_ids[i:i+50]
        request = youtube.videos().list(
            part="snippet",
            id=",".join(chunk_ids)
        )
        response: Dict = request.execute()
        for item in response.get("items", []):
            if "tags" in item["snippet"]:
                tags_map[item["id"]] = item["snippet"]["tags"]
    return tags_map


def write_videos_to_csv(filepath: str, videos_to_add: List[List[str]]) -> None:
    """新しい動画情報をCSVファイルに追記する"""
    write_header = not os.path.exists(filepath)
    with open(filepath, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if write_header:
            header = ["タイトル", "URL", "タグ", "プレイリスト名", "ビデオID", "プレイリストID"]
            writer.writerow(header)
        
        for video in videos_to_add:
            writer.writerow(video)
            
            
def main() -> None:
    """メイン処理"""
    # 1. 設定の読み込み
    settings = load_settings()
    api_key = settings.get("api_key")
    playlist_id = settings.get("playlist_id")
    playlist_name = settings.get("playlist_name")
    csv_filepath = settings.get("csv_filepath")

    if not api_key:
        print("エラー: .envファイルに 'YOUTUBE_API_KEY' を設定してください。")
        return
    if not playlist_id or not playlist_name or not csv_filepath:
        print("エラー: config.iniの設定が不十分です。")
        return

    try:
        # 2. 既存データの取得
        print(f"'{csv_filepath}' を確認中...")
        existing_ids = get_existing_video_ids(csv_filepath)

        # 3. APIで新規データを取得
        print(f"再生リスト「{playlist_name}」の情報を取得中...")
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        
        playlist_items = fetch_playlist_videos(youtube, playlist_id)
        
        new_videos: List[Dict] = []
        new_video_ids: List[str] = []
        for item in playlist_items:
            if "videoId" in item["snippet"]["resourceId"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                if video_id not in existing_ids:
                    new_videos.append({
                        "id": video_id,
                        "title": item["snippet"]["title"],
                        "tags": []
                    })
                    new_video_ids.append(video_id)
        
        if not new_videos:
            print("追加する新しい動画はありませんでした。")
            return

        # タグ情報を取得して追加
        tags_map = fetch_videos_tags(youtube, new_video_ids)
        for video in new_videos:
            if video["id"] in tags_map:
                video["tags"] = tags_map[video["id"]]

        # 4. CSVへの書き込み準備
        rows_to_add: List[List[str]] = []
        for video in new_videos:
            row = [
                video["title"],
                f"https://www.youtube.com/watch?v={video['id']}",
                ", ".join(video["tags"]),
                playlist_name,
                video["id"],
                playlist_id
            ]
            rows_to_add.append(row)

        # 5. CSVファイルへの書き込み
        write_videos_to_csv(csv_filepath, rows_to_add)
        print(f"完了しました。{len(rows_to_add)}件の動画データを '{csv_filepath}' に追加しました。")

    except googleapiclient.errors.HttpError as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
    except IOError as e:
        print(f"ファイル書き込み中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()

# %%
