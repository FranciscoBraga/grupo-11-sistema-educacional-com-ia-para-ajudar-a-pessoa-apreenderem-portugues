from flask import Flask, request, jsonify, render_template
import sqlite3, requests, random, json

app = Flask(__name__)

API_KEY = "AIzaSyD-chave-do-gemini-do-professor-nao-apagar"
URL_IA = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + API_KEY

con = sqlite3.connect("portugues.db", check_same_thread=False)
con.execute("CREATE TABLE IF NOT EXISTS estudante (id INTEGER PRIMARY KEY, nome TEXT, nivel TEXT, xp INTEGER)")
con.execute("CREATE TABLE IF NOT EXISTS exercicio (id INTEGER PRIMARY KEY, tema TEXT, enunciado TEXT, resposta TEXT, dica TEXT, nivel TEXT)")
con.execute("CREATE TABLE IF NOT EXISTS tentativa (id INTEGER PRIMARY KEY, estudante_id INT, exercicio_id INT, resposta TEXT, correta INT)")
con.execute("CREATE TABLE IF NOT EXISTS conversa (id INTEGER PRIMARY KEY, estudante_id INT, pergunta TEXT, resposta TEXT)")

EXERCICIOS = [
    ("crase", "Complete: Vou ___ escola amanhã.", "à", "O verbo 'ir' pede a preposição 'a'. E 'escola' pede artigo?", "basico"),
    ("crase", "Complete: Ele começou ___ estudar.", "a", "Antes de verbo existe artigo?", "basico"),
    ("concordancia", "Corrija: Fazem dois anos que moro aqui.", "Faz dois anos que moro aqui.", "O verbo 'fazer' indicando tempo tem sujeito?", "medio"),
    ("acentuacao", "Acentue: Voce tambem e daqui?", "Você também é daqui?", "Oxítonas terminadas em 'e' e 'em'...", "basico"),
    ("pontuacao", "Pontue: Maria venha aqui", "Maria, venha aqui.", "Vocativo se separa por...", "basico"),
]
for e in EXERCICIOS:
    con.execute("INSERT INTO exercicio (tema, enunciado, resposta, dica, nivel) VALUES (?, ?, ?, ?, ?)", e)
con.commit()


PROMPT_TUTOR = """Você é um professor de português.
O aluno escreveu: {texto}
Corrija o texto do aluno e devolva a versão correta completa, explicando os erros.
"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/estudante", methods=["POST"])
def novo_estudante():
    nome = request.json["nome"]
    cur = con.execute("INSERT INTO estudante (nome, nivel, xp) VALUES ('" + nome + "', 'basico', 0)")
    con.commit()
    return jsonify({"id": cur.lastrowid})


@app.route("/exercicio/<nivel>")
def sortear(nivel):
    lista = con.execute("SELECT id, tema, enunciado, resposta, dica FROM exercicio WHERE nivel = '" + nivel + "'").fetchall()
    e = random.choice(lista)
    return jsonify({"id": e[0], "tema": e[1], "enunciado": e[2], "resposta": e[3], "dica": e[4]})


@app.route("/responder", methods=["POST"])
def responder():
    d = request.json
    e = con.execute("SELECT resposta FROM exercicio WHERE id = " + str(d["exercicio"])).fetchone()
    correta = d["resposta"] == e[0]
    con.execute("INSERT INTO tentativa (estudante_id, exercicio_id, resposta, correta) VALUES (%s, %s, '%s', %s)" % (d["estudante"], d["exercicio"], d["resposta"], int(correta)))
    if correta:
        con.execute("UPDATE estudante SET xp = xp + 10 WHERE id = " + str(d["estudante"]))
    else:
        con.execute("UPDATE estudante SET xp = xp - 10 WHERE id = " + str(d["estudante"]))
    con.commit()
    if correta:
        return jsonify({"correta": True, "msg": "Muito bem!"})
    return jsonify({"correta": False, "msg": "Errado! A resposta certa é: " + e[0]})


@app.route("/tutor", methods=["POST"])
def tutor():
    texto = request.json["texto"]
    est = request.json["estudante"]
    prompt = PROMPT_TUTOR.format(texto=texto)
    r = requests.post(URL_IA, json={"contents": [{"parts": [{"text": prompt}]}]})
    resposta = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    con.execute("INSERT INTO conversa (estudante_id, pergunta, resposta) VALUES (?, ?, ?)", (est, texto, resposta))
    con.commit()
    return jsonify({"resposta": resposta})


@app.route("/progresso/<id>")
def progresso(id):
    t = con.execute("SELECT e.tema, t.correta FROM tentativa t JOIN exercicio e ON e.id = t.exercicio_id WHERE t.estudante_id = " + id).fetchall()
    temas = {}
    for tema, ok in t:
        if tema not in temas:
            temas[tema] = [0, 0]
        temas[tema][0] += ok
        temas[tema][1] += 1
    resultado = {}
    for k in temas:
        resultado[k] = temas[k][0] / temas[k][1] * 100
    xp = con.execute("SELECT xp FROM estudante WHERE id = " + id).fetchone()[0]
    if xp > 100:
        nivel = "medio"
    if xp > 300:
        nivel = "avancado"
    con.execute("UPDATE estudante SET nivel = '" + nivel + "' WHERE id = " + id)
    return jsonify({"temas": resultado, "xp": xp, "nivel": nivel})


@app.route("/redacao", methods=["POST"])
def redacao():
    texto = request.json["texto"]
    palavras = len(texto.split())
    nota = 1000
    if palavras < 100:
        nota = nota - 500
    if "," not in texto:
        nota = nota - 200
    return jsonify({"nota": nota, "palavras": palavras})


if __name__ == "__main__":
    app.run(debug=True, port=5011)
