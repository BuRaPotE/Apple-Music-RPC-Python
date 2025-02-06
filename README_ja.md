# Apple-Music-RPC-Python

<div align="center">
  <img src=https://github.com/user-attachments/assets/c5aa0385-f875-4f49-8ce4-32510d36d95e>
</div>

<p align="center">
  <a href="./README.md"><strong>English</strong></a> | 
  <a href="./README_ja.md"><strong>日本語</strong></a>
</p>

## Description

このリポジトリはPythonでWindows Media APIを利用し、Apple Music の Rich Precenseを表示するためのシンプルなスクリプトです。
Cloudflared のQuick Tunnel を利用してローカルのサムネイルファイルをホスティングし、Discord に画像を送信します。

## Features

- **Apple Music RPC:** Apple Music の再生情報をリアルタイムで取得し、Discord Rich Precense を更新します。Python のみで完結します。
- **サムネイル表示:** Cloudflared のQuick Tunnel を用いて画像をホストし、Rich Precense 上での画像表示をサポートします。
- **Windows Media API :** Apple Music の再生情報を取得するためにWindows Media API をフックしています。プロセス名を変更することにより、ほかのメディアにも対応できます。

## Prerequisites

- Python 3.9 or higher
- Required libraries:
  - `winsdk`
  - `websockets`
  - `Pillow`
  - [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/apple-music-rpc.git
    cd apple-music-rpc
    ```

2. (Optional) Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    cd src
    python3 start.py
    ```

## Usage

Run the start script to start retrieving and sending the playback data:
```bash
cd src
python start.py
```

## Contributing
全ての貢献は歓迎されます！バグ報告や機能の提案、プルリクエストをお待ちしております。

## Acknowledgements
使用させていただいたライブラリやツールの貢献者の方々や、これを作るに至った全ての関係者、そして、winsdk, websockets, Pillow の作者及び貢献者、Cloudflare チームに感謝を表します。

## License

This project is licensed under the [MIT License](./LICENSE).
