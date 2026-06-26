import sqlite3
import pandas as pd

conn = sqlite3.connect('app.db')

print("--- 5 PRIMEIROS PACIENTES ---")
try:
    print(pd.read_sql_query("SELECT * FROM pacientes LIMIT 5", conn))
except Exception as e:
    print("Erro em pacientes:", e)

print("\n--- 5 PRIMEIROS EXAMES SOLICITADOS ---")
try:
    print(pd.read_sql_query("SELECT * FROM exames_solicitados LIMIT 5", conn))
except Exception as e:
    print("Erro em exames_solicitados:", e)

conn.close()