# YouTube再生リスト情報取得ツール

指定したYouTubeの再生リストから動画情報を取得し、CSVファイルとして保存・追記するPythonスクリプトです。

## 概要

このツールは、YouTube Data API v3を利用して、特定の再生リストに含まれる動画の「タイトル」「URL」「タグ」などの情報を自動で収集します。収集したデータはCSVファイルに保存されるため、スプレッドシートなどで簡単に管理・閲覧できます。

一度取得した動画は重複して保存しないため、定期的にスクリプトを実行することで、再生リストに追加された新しい動画だけを効率的に追記していくことが可能です。

## 主な機能

* **再生リスト指定**: `config.ini`ファイルで指定した再生リストから動画情報を取得します。
* **CSVへの保存**: 取得した動画情報を`output`フォルダ内にCSVファイルとして出力します。
* **重複データの除外**: 既にCSVファイルに存在する動画はスキップし、新しい動画のみを追記します。
* **安全なキー管理**: APIキーは`.env`ファイルで管理するため、安全に利用できます。
* **柔軟な設定**: 再生リストIDや出力ファイル名は`config.ini`で簡単に変更可能です。

## 必要なもの

* Python 3.x
* YouTube Data API v3 のAPIキー

## セットアップ手順

1.  **リポジトリをクローン**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **必要なライブラリをインストール**
    ```bash
    pip install -r requirements.txt
    ```

3.  **APIキーを設定**
    `.env.example`ファイルをコピーして`.env`という名前のファイルを作成し、取得したご自身のYouTube Data APIキーを設定してください。
    ```ini
    # .env
    YOUTUBE_API_KEY="ここにあなたのAPIキーを貼り付けてください"
    ```

4.  **取得対象の再生リストを設定**
    `config.ini.example`ファイルをコピーして`config.ini`という名前のファイルを作成し、情報を取得したい再生リストのIDなどを設定してください。  
    playlist_idにはYouTubeのプレイリストID、  
    playlist_nameは保存する際にご自身が分かりやすい名前を付けてください。
    csv_filenameは保存するCSVファイル名を指定してください。
    csvファイルはoutputフォルダに保存されます。
    ```ini
    # config.ini
    [YouTube]
    playlist_id = YOUR_PLAYLIST_ID_HERE
    playlist_name = YOUR_PLAYLIST_NAME_HERE
    csv_filename = movies.csv
    ```

## 使い方

上記セットアップ完了後、ターミナルで以下のコマンドを実行します。

```bash
python get_playlist_videos.py
```

スクリプトが実行されると、`output`フォルダ内に、`config.ini`で指定されたCSVファイルが作成・追記されます。

## 出力されるCSVファイル

`output`フォルダ内に、`config.ini`で指定したファイル名（デフォルトは`movies.csv`）で作成されます。
列の構成は以下の通りです。

| ヘッダー        | 説明                                       |
| --------------- | ------------------------------------------ |
| **タイトル** | 動画のタイトル                             |
| **URL** | 動画への直接リンク                         |
| **タグ** | 動画に設定されているタグ（カンマ区切り）   |
| **プレイリスト名** | `config.ini`で設定した再生リスト名         |
| **ビデオID** | YouTube上のユニークな動画ID                |
| **プレイリストID** | `config.ini`で設定した再生リストID         |

## 作者 (Author)

-   [Thunder](https://github.com/thunderblog)

## ライセンス (License)

このプロジェクトはMITライセンスの下で公開されています。詳細については、`LICENSE`ファイルをご覧ください。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

