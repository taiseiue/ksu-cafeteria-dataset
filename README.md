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

自分で手元の学食営業時間PDFをJSONにするには、以下のコマンドを実行します。実行にはuvか、pdfplumberのインストールが必要です。

```sh
$ uv install
$ python parse_canteen.py <pdf_path> --year 2026 --month 5 --output 2026-05.json
```
