# MTG_17lands_dendrogram

# MTG_17lands_dendrogram

17Lands.comのデータをを使い７勝デッキをまとめ
階層型クラスタリングしてデンドログラムを作るコードです。

使用するデータ
https://www.17lands.com/public_datasets
Game Dataデータ（各自サイトからDL）

或いは
https://www.17lands.com/trophies
からデッキリストを集めて結合した自前のデータ(各自で用意する。）


別途用意するもの（htmlファイルで画像を表示するのに必要）
・imgフォルダ内のカード画像
name_list.tsvでカード名とカード画像ファイル名を紐づけしている。


CSVファイル等の書き換え要素が発生するものはdef main()より上記に記載
セット毎にデータファイル名が違うので各セット毎にファイル名は書き換えする必要あり。
出来るだけ１ファイル内で書き換えを完結したかったので「除外する土地」などの除外カードもpyファイル内に記載してある。
