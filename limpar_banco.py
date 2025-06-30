import sqlite3

conn = sqlite3.connect("agenda_nutri.db")
cursor = conn.cursor()

# Limpar todas as tabelas
cursor.execute("DELETE FROM agenda_nutricionista")
cursor.execute("DELETE FROM agendamentos_pendentes")
cursor.execute("DELETE FROM agendamentos_confirmados")

conn.commit()
conn.close()

print("✅ Banco de dados limpo com sucesso.")
