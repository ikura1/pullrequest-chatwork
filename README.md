# はじめに
バッチ処理の集積しておくリポジトリである。
元々存在していたコードは削除してしまった。
基本的なフォルダ構成は、Flaskの推奨構成と[Pythonプロジェクトのディレクトリ構成](https://www.rhoboro.com/2018/01/25/project-directories.html)を参考にしている。

# 環境変数について
* MONGODB_PORT コンバート用MongoDBポート
* MONGODB_HOST コンバート用MongoDBホスト
* MYSQL_HOST ログ用RDBホスト
* MYSQL_USER ログ用RDBユーザー
* MYSQL_PASSWORD ログ用RDBパスワード
* MYSQL_DB ログ用RDBデータベース名
* MYSQL_PORT ログ用RDBポート

# Makefileについて
元々がconfig.pyに設定が直に書き込まれている形のため、Makefileでの開発・本番実行が制御が行えた。
設定の取得先を環境変数に変更したため、現状がMakefileは機能していない。

なにか良い方法がないか調べる必要がある。

# フォルダ構成
```
.
├── Dockerfile
├── Makefile
├── README.md
├── requirements.lock
├── requirements.txt
├── requirements_dev.txt
└── src
    ├── configs
    │   ├── __init__.py
    │   ├── default.py
    │   ├── config.py
    ├── lib
    │   ├── __init__.py
    │   ├── mongo.py
    │   ├── mysql.py
    │   └── utils.py
    ├── log_server
    │   ├── __init__.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   └── pv_log.py
    │   └── views
    │       ├── __init__.py
    │       └── view.py
    ├── run_log_server.py
    └── scripts
        ├── aggregator_pv.py
        ├── archive_logs.py
        └── convert_logs.py
```