# ksu-cafeteria-dataset
京都産業大学の学食営業時間をまとめたデータ

### What's this?
これは京都産業大学の食堂の営業時間をまとめたデータセットです。
食堂の営業時間PDFをパースし、JSONに整形してから公開しています。

### Usage
データを使うには、以下の形式のUrlにアクセスします。

```
https://taiseiue.github.io/ksu-cafeteria-dataset/data/YYYY-MM.json
```

たとえば、2026年5月のデータを取得するには、以下のUrlにアクセスしましょう。

```
https://taiseiue.github.io/ksu-cafeteria-dataset/data/2026-05.json
```

#### スキーマ定義

スキーマ定義は[docs/schema.md](./docs/schema.md)をご覽ください。以下のようなデータが得られるはずです。
```json
{
  "meta": {
    "year": 2025,
    "month": 5,
    "parsed_at": "2025-05-01T00:00:00Z"
  },
  "stores": [
    {
      "id": 3,
      "name": "らーめん壱馬力",
      "building": "並楽館 1F",
      "hours": [
        { "days": ["mon","tue","wed","thu","fri"], "open_time": "11:00", "close_time": "19:00" },
        { "days": ["sat"], "open_time": "11:00", "close_time": "14:00" }
      ],
      "schedule": {
        "2025-05-01": { "open": true, "open_time": "11:00", "close_time": "17:00" },
        "2025-05-02": { "open": true, "open_time": "11:00", "close_time": "19:00" },
        "2025-05-03": { "open": false }
      }
    }
  ]
}
```


#### 自分でパースする場合
自分で手元の学食営業時間PDFをJSONにするには、以下のコマンドを実行します。実行にはuvか、pdfplumberのインストールが必要です。

```sh
$ uv install
$ python parse_canteen.py <pdf_path> --year 2026 --month 5 --output 2026-05.json
```
