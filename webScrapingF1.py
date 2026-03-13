import json
import os
import time
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import mysql.connector


url = "https://www.formula1.com/en/results/2024/team"

out_path = os.path.join(os.path.dirname(__file__), "ranking.json")

option = Options()

option.headless = True
driver = webdriver.Firefox(options=option)

driver.get(url)

time.sleep(5)
element = driver.find_element(By.TAG_NAME, "table")
html_content = element.get_attribute('outerHTML')


soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find(name='table')

df_full = pd.read_html(StringIO(str(table)))[0].head(10)
df = df_full[['Pos.','Team','Pts.']]
df.columns = ['POS', 'TEAM', 'PTS']

print(df)

ranking = {}
ranking['pts'] = df.to_dict('records')

driver.quit()

with open(out_path, "w", encoding="utf-8") as fp:
    json.dump(ranking, fp, ensure_ascii=False, indent=2)

with open(out_path, encoding="utf-8") as f:
    data = json.load(f)



conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="f1App"
)

cursor = conn.cursor()

for item in data["pts"]:
    sql = "INSERT INTO f1 (pos, team, pts) VALUES (%s,%s,%s)"
    valores = (item["POS"], item["TEAM"], item["PTS"])
    cursor.execute(sql, valores)

conn.commit()
