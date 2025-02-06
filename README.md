# Apple-Music-RPC-Python

<div align="center">
  <img src=https://github.com/user-attachments/assets/811958ff-b480-48e0-86c1-7c49ad606982>
</div>

<p align="center">
  <a href="./README.md"><strong>English</strong></a> | 
  <a href="./README_ja.md"><strong>日本語</strong></a>
</p>

## Description

This repository contains a simple Python script that uses the Windows Media API to display Apple Music Rich Presence. It leverages Cloudflared Quick Tunnel to host local thumbnail files and sends images to Discord.

## Features

- **Apple Music RPC:** Retrieves Apple Music playback information in real time and updates Discord Rich Presence. The entire process is implemented in Python.
- **Thumbnail Display:** Utilizes Cloudflared Quick Tunnel to host images, supporting thumbnail display within Rich Presence.
- **Windows Media API:** Hooks into the Windows Media API to capture playback information from Apple Music. By modifying the process name, the script can be adapted to support other media applications as well.

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
All contributions are welcome! Bug reports, feature suggestions, and pull requests are greatly appreciated.

## Acknowledgements
Special thanks to all the contributors of the libraries and tools used in this project, everyone involved in making this possible, as well as the authors and contributors of winsdk, websockets, Pillow, and the Cloudflare team.

## License

This project is licensed under the [MIT License](./LICENSE).
