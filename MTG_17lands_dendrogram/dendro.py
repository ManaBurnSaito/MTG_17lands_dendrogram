# %%
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from decimal import Decimal

import os
import datetime
import re

# %%
#カレントリディレクト移動、ファイルと同じ場所へ。好みで書き換え
os.chdir(os.path.dirname(os.path.abspath(__file__)))
inputdir = ''#作る場所のフォルダ
d_today = str(datetime.date.today())
outputdir = os.path.join(inputdir, d_today)

# %%
#csv/tsvファイルの読み込み。セット毎に書き換え
csv_file_path = "game_data_public.LTR.PremierDraft.csv" #public_dateのcsvを使用する時
#csv_file_path = "../trophiesROG/trop_resu.tsv" #自前のtsvを使用する時

# %%
#調べたいアーキカラー。好みで書き換え
array_color = ["WU", "WB", "WR", "WG", "UB", "UR", "UG", "BR", "BG", "RG"]
#array_color = ["WB", "WR", "UB", "UR", "BR", "BG"]
#array_color = ["WU", "WG", "UB", "BR", "RG","WUB","WUG","WRG","UBR","BRG"]###SNC###

# %%
#htmlで出力するimgフォルダのpath。htmlのリンク先フォルダのみ。好みで書き換え
html_img_path = "../../../img"

#html出力するカード名とimg名の紐づけtsvのpath。ファイル名も必要。好みで書き換え
tsv_name_path= "../name_list.tsv"

# %%
#除外する土地。セットにより特殊土地を書き換え。
remove_lands_array = [
    'Island',
    'Island.1',
    'Island.2',
    'Island.3',
    'Island.4',
    'Island.5',
    'Island.6',
    'Island.7',
    'Island.8',
    'Island.9',
    'Island.10',
    'Swamp',
    'Swamp.1',
    'Swamp.2',
    'Swamp.3',
    'Swamp.4',
    'Swamp.5',
    'Swamp.6',
    'Swamp.7',
    'Swamp.8',
    'Swamp.9',
    'Swamp.10',
    'Forest',
    'Forest.1',
    'Forest.2',
    'Forest.3',
    'Forest.4',
    'Forest.5',
    'Forest.6',
    'Forest.7',
    'Forest.8',
    'Forest.9',
    'Forest.10',
    'Mountain',
    'Mountain.1',
    'Mountain.2',
    'Mountain.3',
    'Mountain.4',
    'Mountain.5',
    'Mountain.6',
    'Mountain.7',
    'Mountain.8',
    'Mountain.9',
    'Mountain.10',
    'Plains',
    'Plains.1',
    'Plains.2',
    'Plains.3',
    'Plains.4',
    'Plains.5',
    'Plains.6',
    'Plains.7',
    'Plains.8',
    'Plains.9',
    'Plains.10',
    'Barad-dûr',
    'Great Hall of the Citadel',
    'Minas Tirith',
    'Mines of Moria',
    'Mount Doom',
    'Rivendell',
    'Shire Terrace',
    'The Grey Havens',
    'The Shire',
    'Unnamed: 2',
    ]

# %%
#除外するdfのカラム。自前のtsvやpublic_dataの仕様変更により書き換えが発生する必要があるかもしれない。
remove_calam_array = [
    'wins',
    'losses',
    'start_rank',
    'end_rank',
    #'colors',
    'aggregate_id',
    'deck_index',
    'time',
    'has_draft'
    ###public_date###
    'expansion',
    'event_type',
    'draft_id',
    'draft_time',
    'build_index',
    'match_number',
    'game_number',
    'rank',
    'opp_rank',
    #'main_colors',
    'splash_colors',
    'on_play',
    'num_mulligans',
    'opp_num_mulligans',
    'opp_colors',
    'num_turns',
    'won'
    ###public_date###
    ]

# %%
#クラスのインスタンス化とDendrogramの生成
#for aryで色毎に出している。
def main():
    df_trans_obj = DataFrameTransformer(csv_file_path,remove_lands_array,remove_calam_array)
    for cl in array_color:
        for i in range(1, 9):
            count = float(Decimal(i) * Decimal('0.1'))
            df_trans_obj.flt_main_color(cl)
            generator = DendrogramGenerator(df=df_trans_obj.df_color, outputdir=outputdir, color=cl, threshold=count, file_type=df_trans_obj.file_extension)
            generator.generate_dendrogram()
            generator.save_dendrogram_labels()
            generator.create_html_output(namelist_path=tsv_name_path)

# %%
class DataFrameTransformer:
    """
    データフレームの前処理

    Parameters:
        df (pandas.DataFrame):前処理を行うデータフレーム
        color (str): 調べたいアーキカラー["WU", "WB", "WR", "WG", "UB", "UR", "UG", "BR", "BG", "RG"]
        ary_lands (list): dfから除外する土地カードなどの配列
        ary_calam (list): dfから除外するカード以外のカラム(ドラフトID等)

    """
    def __init__(self, csv_file_path, rem_lands_ary, rem_calam_ary) -> None:
        self.file_extension = None
        self.df = self.read_file_to_df(csv_file_path)
        self.df_color = None
        #self.df = df
        self.ary_lands = rem_lands_ary #dfから除外する土地カード等
        self.ary_calam = rem_calam_ary #dfから除外するカード以外のカラム(ドラフトID等)
        
        
        if self.file_extension  == "csv":
            self.df = self.rename_df(self.df)
            self.df = self.public_date_dfmolding(self.df)

        if self.file_extension  == "tsv":
            self.df = self.dfmolding(self.df)


    #def main(self):
    #    self.df = self.dfmolding(df)

    def read_file_to_df(self, csv_file_path) -> pd.DataFrame:
        # ファイルの拡張子を取得
        file_extension = csv_file_path.split(".")[-1]

        # TSVファイルの場合
        if file_extension == "tsv":
            self.file_extension = "tsv"
            df = pd.read_table(csv_file_path, encoding='utf-8-sig')
            # タッチカラーの小文字削除
            df['colors'] = df['colors'].apply(lambda x: re.sub(r'[a-z]', '', x))

        # CSVファイルの場合
        elif file_extension == "csv":
            self.file_extension = "csv"
            # 分割する行数を指定する
            chunksize = 100000
            # 空のリストを作成して、分割したデータを一時的に保存する
            chunks = []
            
            # CSVファイルを分割して読み込み、一時的にリストに保存する
            for chunk in pd.read_csv(csv_file_path, encoding='utf-8-sig', chunksize=chunksize):
                chunks.append(chunk)
            
            # すべてのデータを結合して、一つのデータフレームに戻す
            df = pd.concat(chunks)

        else:
            raise ValueError("Unsupported file format. Only 'tsv' and 'csv' formats are supported.")
        
        return df


    #public_dateを読み込んだdfの成形
    def public_date_dfmolding(self,df) -> pd.DataFrame: 
        df = self.df_groupby(df)
        df = self.deck_del(df)
        df = self.del_columns_name(df)
        df = self.remove_calam(df,self.ary_calam)
        df = self.remove_calam_lands(df,self.ary_lands)
        return df

    #自前のtsvを読み込んだdfの成形
    def dfmolding(self,df) -> pd.DataFrame: 
        df = self.remove_calam(df,self.ary_calam)
        df = self.remove_calam_lands(df,self.ary_lands)
        return df

    def deck_del(self,df):
        #######deck_の列だけ抽出する#########
        # 対象となる文字列
        character = 'deck_'
        # 対象文字列を含む列名を取得
        column_inc_specific_char = [column for column in df.columns if character in column]

            # 'colors'カラムも追加
        if 'colors' in df.columns:
            column_inc_specific_char.append('colors')

        # 取得した列名のみのデータフレーム
        df = df[column_inc_specific_char]
        return df

    #指定したカラムの削除・start_rank等のカード名ではないカラムの削除
    def remove_calam(self,df,remove_array):
        to_remove_word_calam = remove_array
        df = df[df.columns.difference(to_remove_word_calam)]
        return df

    #指定したカラムの削除・主に土地カードの削除    
    def remove_calam_lands(self,df,array):
        df = df[df.columns.difference(array)]
        return df
    
    def df_groupby(self,df):
        df = df[df['won']]
        df = df.groupby(['draft_id','colors'], as_index=False).sum()
        df = df.query('won == 7')
        return df
    
    def del_columns_name(self,df):
        df.columns = df.columns.str.replace('deck_', '')
        return df

    def flt_main_color(self, color):
        self.df_color = self.df[self.df['colors'] == color]
        self.df_color = self.df_color.drop(columns=['colors'])

    def rename_df(self,df):
        return df.rename(columns={'main_colors':'colors'})

# %%
class DendrogramGenerator:
    """
    階層型クラスタリングしてデンドログラムを作る。

    Parameters:
        df (pandas.DataFrame):調べたいDF
        outputdir(str):出力ディレクトリのパス
        threshold (float): 閾値:これ以下の回数のカードを除外する。例:20%以下を除外する
        color (str): 調べたいアーキカラー["WU", "WB", "WR", "WG", "UB", "UR", "UG", "BR", "BG", "RG"]
        dendrogram :hierarchy.dendrogram(linkage, labels=filt_df.columns, orientation='right')の結果の格納
    """
    def __init__(self, df, outputdir, color,threshold,file_type):
        self.threshold = threshold
        self.df = df
        self.outputdir = outputdir
        self.file_type = file_type
        self.dendrogram = None
        self.color = color
        
    def generate_dendrogram(self):
        index_count = len(self.df.index)
        #出現回数のフィルター設定、回数：index_countの20%未満のカードを非表示にする
        if self.file_type == "csv":
            threshold_value = float(index_count * self.threshold * 7)
            filt_df = self.df.loc[:, self.df.sum() > threshold_value]
        else:
            threshold_value = float(index_count * self.threshold)
            filt_df = self.df.loc[:, self.df.sum() > threshold_value]


        ax = plt.figure(figsize=(18,10)).gca()
        linkage = hierarchy.linkage(filt_df.values.T, method="ward")
        self.dendrogram = hierarchy.dendrogram(linkage, labels=filt_df.columns, orientation='right')

        #plt.rcParams["figure.figsize"] = (18, 10)
        plt.xticks(rotation=90)
        plt.ylabel("card_name", fontsize=18)
        plt.xlabel("cls_distance", fontsize=18)
        plt.title(f'{self.color}_{self.threshold}', fontsize=18)

 
        if not os.path.exists(self.outputdir):
            os.mkdir(self.outputdir)

        if not os.path.exists(f'{self.outputdir}/{self.threshold}'):
            os.mkdir(f'{self.outputdir}/{self.threshold}')
        plt.savefig(f'{self.outputdir}/{self.threshold}/dendro_{self.color}_{self.threshold}.png', facecolor='white', pad_inches=0.1)
        plt.close('all')
        #plt.show()

    #デンドログラムのラベルをテキスト出力
    def save_dendrogram_labels(self):
        if self.dendrogram is not None:
            labels = self.dendrogram["ivl"]
            with open(f"{self.outputdir}/{self.threshold}/{self.color}_{self.threshold}_labels.txt", "w",encoding='utf-8-sig') as file:
                for i in labels:
                    file.write(f"{i}\n")

    #デンドログラムの色分けの区分をテキストに出す。ほぼテスト用
    def save_dendrogram_color(self):
        if self.dendrogram is not None:
            labels = self.dendrogram["leaves_color_list"]
            with open(f"{self.outputdir}/{self.threshold}/{self.color}_{self.threshold}_label_color.txt", "w",encoding='utf-8-sig') as file:
                for i in labels:
                    file.write(f"{i}\n")

    #デンドログラムのラベルにあるカードをHTMLファイルに出力。
    def create_html_output(self, namelist_path):
        if self.dendrogram is not None:
            labels = self.dendrogram["ivl"]
            label_color =  self.dendrogram["leaves_color_list"]
            data = {'name': labels, 'label_color': label_color}
            df_deck = pd.DataFrame(data)

            namelist = pd.read_table(namelist_path,encoding='utf-8-sig')
            join_data = pd.merge(df_deck, namelist, on="name", how="inner")

            html = []
            for ht in join_data.itertuples():
                html.insert(0,f'<B><div class={ht.label_color}><img src="{html_img_path}/{str(ht.img)}" width="160"/><div class=NAME>{ht.name}</div></div><B>\n')

            html.insert(0,f'<html><head><title>dendrogram</title><link rel="stylesheet" type="text/css" href="../../common.css"></head><body><A>dendrogram_{self.color}_{self.threshold}</A><br />\n')
            html.append('</body></html>')
            html_code = ''.join(html)

            with open(f'{self.outputdir}/{self.threshold}/{self.color}.html', 'w', encoding='utf-8') as file:
                file.write(html_code)

# %%
if __name__ == "__main__":
    main()


