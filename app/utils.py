def calcular_tmb(peso, altura, idade, sexo="masculino"):
    """
    Calcula a Taxa Metabólica Basal usando a fórmula de Harris-Benedict
    """
    altura_cm = altura * 100

    if sexo == "masculino":
        tmb = 88.362 + (13.397 * peso) + (4.799 * altura_cm) - (5.677 * idade)
    else:
        tmb = 447.593 + (9.247 * peso) + (3.098 * altura_cm) - (4.330 * idade)

    return round(tmb)


def calcular_gasto_profissional(tmb, profissao):
    """
    Calcula o gasto calórico baseado na profissão
    Estoquista = atividade moderada = 35% adicional
    """
    multiplicadores = {
        "sedentario": 0.2,  # 20% adicional
        "leve": 0.375,  # 37.5% adicional
        "moderado": 0.55,  # 55% adicional (Estoquista)
        "intenso": 0.725,  # 72.5% adicional
        "muito_intenso": 0.9,  # 90% adicional
    }

    if "estoquista" in profissao.lower():
        return round(tmb * multiplicadores["moderado"])

    return round(tmb * multiplicadores["moderado"])  # Padrão moderado


def calcular_calorias_refeicao(periodo, proteina=None):
    """
    Retorna as calorias de cada refeição
    """
    refeicoes = {
        "Café da Manhã": 350,
        "Almoço": 320,  # base sem proteína
        "Lanche da Tarde": 180,
        "Janta": 280,  # base sem proteína
        "Ceia": 100,
    }

    proteinas = {
        "Frango grelhado 150g": 230,
        "Carne vermelha magra 120g": 250,
        "Carne de porco magra 120g": 260,
        "Frango desfiado 120g": 184,
        "Carne vermelha 100g": 208,
        "Carne de porco 100g": 217,
    }

    calorias_base = refeicoes.get(periodo, 0)

    if proteina and proteina in proteinas:
        return calorias_base + proteinas[proteina]

    return calorias_base
