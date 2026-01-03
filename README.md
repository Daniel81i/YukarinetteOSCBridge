# このリポジトリは開発中であり、動作しません
# YukarinetteOSCBridge

<p align="center">
  <a href="./assets/YukarinetteOSCBridge.png">
    <img src="https://img.shields.io/github/license/colasama/reboslime" alt="license">
  </a>
  <img src="https://img.shields.io/badge/python-3.12.x-blue?logo=python&logoColor=edb641" alt="python">
</p>

YukarinetteOSCBridge は、**ゆかりねっとコネクター Neo をOSC経由でVRChat内から操作するするアプリ**です。タスクトレイに常駐し、OSCからのコマンドを受信します。

---

## ✨ 主な機能

### ✔ OSC 受信
- VRChat からのゆかりねっとコネクター Neo 設定変更コマンドをOSC で受信
- コマンドはミュート、翻訳言語変更に対応

### ✔ ゆかりねっとコネクター Neo API 送信
- ゆかりねっとコネクター Neo へ設定変更APIを送信
- ゆかりねっとコネクター Neoの仕様に従いレジストリから http のポート番号を自動取得（DWORD の場合は `http://127.0.0.1:PORT` として組み立て）

### ✔ アプリケーションログ exe 名に合わせたグファイル名
- YukarinetteOSCBridge.exe → YukarinetteOSCBridge.log

### ✔ タスクトレイ常駐
- WebSocket の状態をツールチップで表示  
  - 接続待機中  
  - 接続中  
  - 受信中  
  - 再接続中  
  - 切断  
- 右クリックメニューに Exit（終了）を表示

### ✔ Windows 通知
- 起動時  
- 再接続失敗時  

### ✔ 終了検知
- 監視プロセスが存在しない場合

---

## 📦 インストール方法

### 1. Release から ZIP をダウンロード
```
YukarinetteOSCBridge.zip
├─ YukarinetteOSCBridge.exe
└─ config.json
```

### 2. 任意のフォルダに展開

### 3. config.json を編集（必要に応じて）
```json
{
  // デバッグログ出力
  "DEBUG": false,

  // OSC ポート設定
  "OSC_RECV_PORT": 9000,
  "OSC_SEND_PORT": 9001,

  // OSC パス（受信は1つ、送信は3つ）
  "OSC_PATH_RECV": "/avatar/parameters/Translator/Yukakone/Input",
  "OSC_PATH_SEND_MUTE": "/avatar/parameters/Translator/Yukakone/Mute",
  "OSC_PATH_SEND_LANGID": "/avatar/parameters/Translator/Yukakone/TranslationId",
  "OSC_PATH_SEND_RETCODE": "/avatar/parameters/Translator/Yukakone/retcode",

  // ゆかりねっとコネクター Neo API（固定パス）
  "YUKACONE_MUTE_ON": "/api/mute-on",
  "YUKACONE_MUTE_OFF": "/api/mute-off",
  "YUKACONE_LANGID_BASE": "/api/setTranslationParam?slot=1",

  // 言語設定のプリセット（10パターンまで登録可能）
  "LANG_PRESETS": [
    { "ItemNo": 1, "language": "en-US", "engine": "microsoft" },
    { "ItemNo": 2, "language": "de-DE", "engine": "google" },
    { "ItemNo": 3, "language": "pt-BR", "engine": "google" },
    { "ItemNo": 4, "language": "fr-FR", "engine": "google" },
    { "ItemNo": 5, "language": "fi-FI", "engine": "google" },
    { "ItemNo": 6, "language": "zh-CN", "engine": "google" },
    { "ItemNo": 7, "language": "ko-KR", "engine": "google" },
    { "ItemNo": 8, "language": "en-US", "engine": "google" },
  ],

  // ゆかりねっとコネクター Neo API のレジストリ情報
  "REGISTRY_HIVE": "HKEY_CURRENT_USER",
  "REGISTRY_PATH": "SOFTWARE\\YukarinetteConnectorNeo",
  "REGISTRY_VALUE_HTTP": "http",

  // ゆかりねっとコネクター Neo プロセス監視、監視間隔
  "TARGET_PROCESS": "YNC_Neo.exe",
  "PROCESS_CHECK_INTERVAL_SEC": 5
}
```
### config.json の各項目について

| 項目名 | 説明 |
|--------|------|
| `DEBUG` | デバッグモード。true にするとログが詳細になる。 |
| `OSC_RECV_PORT` | OSC の受信ポート番号。 |
| `OSC_SEND_PORT` | OSC の送信ポート番号（VRChatが受信するポート番号）。 |
| `OSC_PATH_RECV` | コマンド受信パラメータ。 |
| `OSC_PATH_SEND_MUTE` | コマンド設定結果の値（ミュート）。 |
| `OSC_PATH_SEND_LANGID` | コマンド設定結果の値（言語切り替え）。 |
| `OSC_PATH_SEND_RETCODE` | コマンド実行結果の値。 |
| `YUKACONE_MUTE_ON` | ゆかりねっとコネクター Neo　API　ミュートオン。 |
| `YUKACONE_MUTE_OFF` | ゆかりねっとコネクター Neo　API　ミュートオフ。 |
| `YUKACONE_LANGID_BASE` | ゆかりねっとコネクター Neo　API　言語切り替え。 |
| `LANG_PRESETS` | 言語切り替え設定（最大8）。 |
| `LANG_PRESETS.ItemNo` | 言語切り替えNo.。 |
| `LANG_PRESETS.language` | 翻訳言語。 |
| `LANG_PRESETS.engine` | 翻訳エンジン。 |
| `REGISTRY_HIVE` | OSC のポート番号を取得するレジストリのハイブ。通常は `HKEY_CURRENT_USER`。 |
| `REGISTRY_PATH` | OSC のポート番号が保存されているレジストリパス。 |
| `REGISTRY_VALUE_HTTP` | レジストリ内の値の名前。DWORD の場合はポート番号として扱う。 |
| `TARGET_PROCESS` | 監視プロセス名`。 |
| `PROCESS_CHECK_INTERVAL_SEC` | プロセス監視間隔（s）。 |

### 4. YukarinetteLogger.exe を起動  
タスクトレイにアイコンが表示されます。

---

## 📝 レジストリ設定について

ゆかりねっとコネクター Neoの仕様に従いhttp のポート番号はレジストリから取得します。
HKCU\Software\YukarinetteConnectorNeo\http

### ✔ DWORD（数値）
ポート番号として扱い、以下の URL を自動生成します。
```
ws://127.0.0.1:{PORT}
```

---

## 🛠 ビルド方法（開発者向け）

### 1. 依存関係をインストール
```
pip install -r requirements.txt
```

### 2. PyInstaller でビルド
```
pyinstaller --onefile --noconsole --name YukarinetteLogger main.py osc_handler.py tray.py yukari_api.py
```

### 3. config.json を dist フォルダへコピー
```
copy config.json dist\
```

---

## 🚀 GitHub Actions（自動ビルド & Release）

- タグ（例：v1.0.0）を push すると自動ビルド  
- YukarinetteLogger.exe と config.json を ZIP 化  
- YukarinetteLogger.zip として Release にアップロード  

---

## 📄 ライセンス

MIT License

---

## 🙏 作者より

このツールは、ゆかりねっとコネクター Neo をより便利に使うための **ゆかりねっとコネクター Neo をOSC経由でVRChat内から操作するするアプリ**として開発されました。改善案・要望・バグ報告などあれば Issue へどうぞ。
