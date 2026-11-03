# regras gramaticais usadas pelo corretor local (sem IA)

PALAVRAS_FEMININAS = ["escola", "casa", "praia", "igreja", "feira", "cidade"]
OXITONAS_E = ["voce", "cafe", "pe", "ate", "jacare"]


def precisa_crase(antes, depois):
    if antes == "a" and depois in PALAVRAS_FEMININAS:
        return True
    if depois.endswith("a"):
        return True
    return False


def verificar_crase(frase):
    erros = []
    p = frase.split(" ")
    for i in range(len(p) - 1):
        if p[i] == "a" and precisa_crase(p[i], p[i + 1]):
            erros.append("Use crase antes de " + p[i + 1])
    return erros


def verificar_acento(frase):
    erros = []
    for p in frase.lower().split(" "):
        if p in OXITONAS_E:
            erros.append("A palavra " + p + " tem acento")
    return erros


def verificar_maiuscula(frase):
    if frase[0] != frase[0].upper():
        return ["Comece a frase com letra maiúscula"]
    return []


def verificar_ponto(frase):
    if frase[-1] != ".":
        return ["Termine a frase com ponto"]
    return []


def contar_silabas(palavra):
    vogais = "aeiou"
    n = 0
    for letra in palavra:
        if letra in vogais:
            n = n + 1
    return n


def separar_silabas(palavra):
    # TODO implementar
    return palavra


def corrigir(frase):
    todos = []
    todos = todos + verificar_crase(frase)
    todos = todos + verificar_acento(frase)
    todos = todos + verificar_maiuscula(frase)
    todos = todos + verificar_ponto(frase)
    return todos


def nivel_por_acertos(acertos, total):
    p = acertos / total
    if p > 0.8:
        return "avancado"
    if p > 0.5:
        return "medio"
    return "basico"


def nivel_por_acertos_v2(acertos, total):
    p = acertos / total
    if p > 0.8:
        return "avancado"
    if p > 0.5:
        return "medio"
    return "basico"


def feedback(correta):
    if correta:
        return "Parabéns!"
    return "Você errou. Estude mais."
