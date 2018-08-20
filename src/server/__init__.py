# -*- coding: utf-8 -*-
from flask import Flask
# 大本のFlaskの宣言とconfigの読み込み
app = Flask(__name__)
app.config.from_object('server.config')
from server import view

# Blueprintで記述したAPIをflaskに追加していく
modules_define = [view.app]
for view in modules_define:
    app.register_blueprint(view)
