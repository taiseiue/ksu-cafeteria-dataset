# JSONスキーマ定義

`data/YYYY-MM.json` のスキーマ定義です。

## トップレベル

| フィールド | 型 | 説明 |
|---|---|---|
| `meta` | object | ファイルのメタ情報 |
| `stores` | array\<Store\> | 店舗一覧 |

## `meta`

| フィールド | 型 | 例 | 説明 |
|---|---|---|---|
| `year` | number | `2025` | 対象年 |
| `month` | number | `5` | 対象月 |
| `parsed_at` | string (ISO 8601) | `"2025-05-01T00:00:00Z"` | パース日時 (UTC) |

## `Store`

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | number | PDF上の通し番号 |
| `name` | string | 店舗名（全角英数字を半角に正規化済み） |
| `building` | string | 建物・フロア（例: `"10号館 1F"`） |
| `hours` | array\<Hours\> | 定常営業時間（曜日ごと）。`schedule` の補完元にも使用 |
| `schedule` | object\<date, DayEntry\> | 日付ごとの営業状態。キーは `YYYY-MM-DD` 形式 |

## `Hours`

定常営業時間を曜日単位で表します。曜日によって閉店時間が異なる場合（例: 水曜短縮）は複数エントリになります。

| フィールド | 型 | 例 | 説明 |
|---|---|---|---|
| `days` | array\<string\> | `["mon","tue","wed","thu","fri"]` | 対象曜日。`mon` `tue` `wed` `thu` `fri` `sat` `sun` |
| `open_time` | string | `"11:00"` | 開店時刻 (`HH:MM`) |
| `close_time` | string | `"15:00"` | 閉店時刻 (`HH:MM`) |

## `DayEntry`

1日の営業状態を表します。`open: false` の日は他フィールドを持ちません。

| フィールド | 型 | 説明 |
|---|---|---|
| `open` | boolean | 営業するか否か |
| `open_time` | string? | 開店時刻 (`HH:MM`)。`open: true` かつ通常営業の場合に存在 |
| `close_time` | string? | 閉店時刻 (`HH:MM`)。`open: true` かつ通常営業の場合に存在 |
| `note` | string? | 特記事項（例: `"パンのみ"`）。時刻の代わりに存在する場合がある |

### `DayEntry` パターン例

```jsonc
// 通常営業(時刻はhoursか、曜日ごとの定時)
{ "open": true, "open_time": "11:00", "close_time": "14:00" }

// 休業
{ "open": false }

// 特殊営業（時刻なし、メモあり）
{ "open": true, "note": "パンのみ" }
```

### 時刻の優先順位

`schedule` の時刻は以下の優先順位で決まります。

1. PDFに時刻が明記されている場合は、その値をそのまま使用
2. 時刻は明記されていないが、営業の場合は曜日ごとの営業時間を引く
3. 営業時間が不明な場合はなし

## サンプル

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
