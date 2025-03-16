
import pymysql
import json

# Connexion à la base de données
conn = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="chatbot"
)

cursor = conn.cursor()

# Exécution de la requête
query = """
SELECT 
    e.id AS element_id,
    e.name AS element_name,
    t.fname AS prof_first_name,
    t.lname AS prof_last_name,
    m.name AS module_name,
    s.name AS semester_name,
    sec.name AS sector_name
FROM element e
JOIN teacher t ON e.prof_id = t.id
JOIN module m ON e.module_id = m.id
JOIN semester s ON m.semester_id = s.id
JOIN sector sec ON s.sector_id = sec.id;

"""

cursor.execute(query)
data = cursor.fetchall()

# Conversion en JSON
columns = [col[0] for col in cursor.description]
result_json = [dict(zip(columns, row)) for row in data]
# Affichage du JSON
print(json.dumps(result_json, indent=4, ensure_ascii=False))
# Sauvegarde en fichier JSON
with open("structure.json", "w", encoding="utf-8") as f:
    json.dump(result_json, f, indent=4, ensure_ascii=False)

cursor.close()
conn.close()
