let estudante = null
let exercicio = null

function postar(url, dados) {
  return fetch(url, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(dados)}).then(r => r.json())
}

function comecar() {
  postar("/estudante", {nome: document.getElementById("nome").value}).then(d => {
    estudante = d.id
    proximo()
  })
}

function proximo() {
  fetch("/exercicio/basico").then(r => r.json()).then(e => {
    exercicio = e
    document.getElementById("tema").innerText = e.tema
    document.getElementById("enunciado").innerText = e.enunciado
    document.getElementById("resposta").value = ""
    document.getElementById("feedback").innerText = ""
    document.getElementById("dica").innerText = ""
    console.log("resposta:", e.resposta)
  })
}

function responder() {
  let r = document.getElementById("resposta").value
  postar("/responder", {estudante: estudante, exercicio: exercicio.id, resposta: r}).then(d => {
    document.getElementById("feedback").innerText = d.msg
    document.getElementById("feedback").style.color = d.correta ? "green" : "red"
  })
}

function verDica() {
  document.getElementById("dica").innerText = exercicio.resposta
}

function perguntarTutor() {
  let t = document.getElementById("textoTutor").value
  document.getElementById("respTutor").innerHTML = "pensando..."
  postar("/tutor", {texto: t, estudante: estudante}).then(d => {
    document.getElementById("respTutor").innerHTML = d.resposta
  })
}

function verProgresso() {
  fetch("/progresso/" + estudante).then(r => r.json()).then(p => {
    let h = "<p>Nível: " + p.nivel + " | XP: " + p.xp + "</p>"
    for (let t in p.temas) {
      h += "<div class='barra'><span style='width:" + p.temas[t] + "%'></span>" + t + " " + p.temas[t] + "%</div>"
    }
    document.getElementById("progresso").innerHTML = h
    document.getElementById("xp").innerText = p.xp + " XP"
  })
}
