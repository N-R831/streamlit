import streamlit as st
import datetime
import sqlite3
import pandas as pd 

dbname = 'MASTER.db'


date = st.date_input('日付を入力してください。', datetime.date.today())
input_num = st.number_input('回数を入力してください', value=0)

# 平均値の取得
conn = sqlite3.connect(dbname)

# テーブルを作成する 
conn.execute('''
CREATE TABLE IF NOT EXISTS master_dt ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    date TEXT NOT NULL,
    master_num INTEGER NOT NULL
) 
''')

str_sql = 'SELECT avg(master_num) FROM master_dt'
# sqliteを操作するカーソルオブジェクトを作成
cur = conn.cursor()
cur.execute(str_sql)
ret = cur.fetchall()
ave = ret[0]
st.write('Average: ', ave)

if st.button('start'):
    date_str = date.strftime('%Y-%m-%d')
    result = input_num
    str_sql = "INSERT INTO master_dt (date, master_num) values(" + f"'{date_str}'" + ", " + f'{result}' + ")"
    cur.execute(str_sql)
    
    # データベースへコミット。これで変更が反映される。
    conn.commit()

# 統計データの表示
df = pd.read_sql_query(f'''
SELECT date, master_num
FROM master_dt
''', conn)

if not df.empty:
    st.header('平均')

avg_num = df['master_num'].mean()

st.write(f'{avg_num:.1f}')

#conn.close()