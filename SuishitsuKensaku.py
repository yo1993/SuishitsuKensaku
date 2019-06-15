#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""「任意期間水質検索」サイトデータ  取得
指定された 観測所記号 のデータ(1970~2018年分)をCSV形式で保存
"""


# ==== ライブラリ ====

import os
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from io import StringIO


# ====定数 ====

# 開始年
BGNYEAR_INT = 1970

# 終了年
ENDYEAR_INT = 2018

# ？
KIND_STR = "1"

# 観測所記号
ID_STR = "409141289916120"  # 柳瀬橋（やなせばし）

# 項目選択
# KIJUN_STR = ""  # 可変にする

# 開始日付(YYYYMMDD)
# BGNDATE_STR = ""  # 可変にする

# 終了日付(YYYYMMDD)
# ENDDATE_STR = ""  # 可変にする

# ？
KAWABOU_STR = "NO"

# 出力フォルダ名
dir_path = "dat"

# インデックスページのURL
# ※datファイルパス：http://www1.river.go.jp/dat/dload/download/~.dat
INDEX_URL = "http://www1.river.go.jp"

# DspWquaData.exe のURL
EXE_URL = \
    "http://www1.river.go.jp/cgi-bin/DspWquaData.exe?" \
    "KIND=KindStr&" \
    "ID=IdStr&" \
    "KIJUN=KijunStr&" \
    "BGNDATE=BgnDateStr&" \
    "ENDDATE=EndDateStr&" \
    "KAWABOU=KawabouStr"

# header
ARR_HDR1 = "年月日,時分,採水位置,採水時刻(時分),採水位置," \
          "天候,水位(ｍ),流量(m3/sec),全水深(ｍ),採水水深(ｍ)," \
          "気温(℃),水温(℃),外観（１）,外観（２）,外観（３）," \
          "外観（４）,臭気（冷時）,透視度(cm),透明度(ｍ),干潮時刻(時分)," \
          "満潮時刻(時分)\n"
ARR_HDR2 = "年月日,時分,採水位置,ｐＨ,ＢＯＤ(mg/L)," \
           "ＣＯＤ(mg/L),ＳＳ(mg/L),ＤＯ(mg/L),ＤＯ飽和度(％),大腸菌群数（１）(MPN/100mL)," \
           "ｎ－ヘキサン抽出物質(油分)(mg/L),総窒素(mg/L),総リン(mg/L)\n"


# ==== ここからスタート ====
if __name__ == '__main__':

    print("start")

    # 01:現地観測項目, 02:生活環境の保全に関する環境基準項目
    for kijun_str in ["01", "02"]:

        # ファイルに出力する文字列初期値
        if kijun_str == "01":
            str_res = ARR_HDR1
        elif kijun_str == "02":
            str_res = ARR_HDR2

        # 対象期間に対してループ
        for year_idx in range(BGNYEAR_INT, ENDYEAR_INT + 1):

            # 開始・終了日付文字列
            bgn_date = str(year_idx) + "0101"
            end_date = str(year_idx) + "1231"

            # DspWquaData.exe のURL
            exe_url = EXE_URL.replace("KindStr", KIND_STR)\
                .replace("IdStr", ID_STR)\
                .replace("KijunStr", kijun_str)\
                .replace("BgnDateStr", bgn_date)\
                .replace("EndDateStr", end_date)\
                .replace("KawabouStr", KAWABOU_STR)

            # ページをhttpレスポンスとして取得
            http_res = urllib.request.urlopen(exe_url)

            # htmlをBeautifulSoupで扱う
            beaut_soup = BeautifulSoup(http_res, "html.parser")

            # <iframe>タグを取得
            iframe_tag = beaut_soup.iframe

            # src属性値の取得
            tar_url_rel = iframe_tag.attrs["src"]

            # 相対パスを絶対パスに変更
            tar_url = INDEX_URL + tar_url_rel

            # ページ内の表をデータフレームのリストに変換して取得
            df_list = pd.io.html.read_html(tar_url)

            # numpy arrayとして値だけ取得
            arr_orig = df_list[0].values.astype(str)

            # 1行目はヘッダーなので消す
            arr_dat = np.delete(arr_orig, 0, axis=0)

            # numpy arrayをCSV文字列に変換(nanも消しておく)
            f_strm = StringIO()
            np.savetxt(f_strm, arr_dat, fmt="%s", delimiter=",")
            csv_str_orig = f_strm.getvalue()
            csv_str = csv_str_orig.replace("nan", "")
            str_res = str_res + csv_str

            print(kijun_str + "_" + str(year_idx) + " " + "end")

        # csvファイルのパス
        f_path = dir_path + "/" + ID_STR + "_" + kijun_str + ".csv"

        # フォルダ一応作っておく
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        # csvファイルに出力
        with open(f_path, mode='w') as f:
            f.write(str_res)

    print("end")
