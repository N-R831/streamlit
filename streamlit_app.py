import streamlit as st
import datetime
import sqlite3
import pandas as pd
import os

# データベース接続
# 環境変数からデータベースのパスを取得
db_path = os.getenv("DATABASE_URL")
dbname = r'C:\Users\ryohm\work\11_python\git\streamlit\db\MASTER.db'
# データベースに接続
if db_path:
    conn = sqlite3.connect(db_path)
else:
    conn = sqlite3.connect(dbname)
cur = conn.cursor()

selected_data = st.sidebar.selectbox('メニュー', ['Edit', 'Record'])

if selected_data == 'Edit':
    date = st.date_input('日付を入力してください。', datetime.date.today())
    input_num = st.number_input('回数を入力してください', value=0)


    # テーブルを作成する 
    conn.execute('''
    CREATE TABLE IF NOT EXISTS master_dt ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        date TEXT NOT NULL,
        master_num INTEGER NOT NULL
    ) 
    ''')

    str_sql = 'SELECT avg(master_num) FROM master_dt'
    cur.execute(str_sql)
    ret = cur.fetchall()
    ave = ret[0]

    if st.button('submit'):
        date_str = date.strftime('%Y-%m-%d')
        result = input_num
        # 存在チェック
        df = pd.read_sql(f'''
            SELECT master_num
            FROM master_dt
            WHERE date = "{date_str}"
            ''', conn)
        if not df.empty:
            str_sql = "UPDATE  master_dt SET master_num=" + f'{result}'+ " WHERE DATE=" + f"'{date_str}'"
        else:
            str_sql = "INSERT INTO master_dt (date, master_num) values(" + f"'{date_str}'" + ", " + f'{result}' + ")"
        cur.execute(str_sql)
        
        # データベースへコミット。これで変更が反映される。
        conn.commit()
elif selected_data == 'Record':
    # 統計データの表示
    df = pd.read_sql(f'''
    SELECT date, master_num
    FROM master_dt
    ORDER BY date DESC
    ''', conn)


    if not df.empty:
        st.header('平均')
        avg_num = df['master_num'].mean()

        st.write(f'{avg_num:.3f}')
        st.dataframe(df)

#conn.close()