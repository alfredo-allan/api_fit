from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    User,
    MetaPeso,
    AtividadeFisica,
    RotinaAlimentar,
    CaloriasExtras,
)
from app.utils import calcular_tmb, calcular_gasto_profissional
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_dashboard():
    """
    Retorna todos os dados consolidados para o dashboard.
    Inclui:
        - Dados do usuário
        - Última meta
        - Atividade do dia
        - Consumo alimentar
        - Calorias extras
        - Balanço calórico completo
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        hoje = date.today()

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        # -----------------------------------------------------------
        # META (pega a mais recente)
        # -----------------------------------------------------------
        ultima_meta = (
            MetaPeso.query.filter_by(user_id=user_id)
            .order_by(MetaPeso.data_registro.desc())
            .first()
        )

        # -----------------------------------------------------------
        # ATIVIDADE DO DIA
        # -----------------------------------------------------------
        atividade = AtividadeFisica.query.filter_by(user_id=user_id, data=hoje).first()

        # -----------------------------------------------------------
        # CALORIAS EXTRAS DO DIA
        # -----------------------------------------------------------
        extras = CaloriasExtras.query.filter_by(user_id=user_id, data=hoje).all()

        # -----------------------------------------------------------
        # ROTINA ALIMENTAR DO DIA
        # -----------------------------------------------------------
        rotinas = RotinaAlimentar.query.filter_by(user_id=user_id, data=hoje).all()

        # -----------------------------------------------------------
        # CÁLCULOS DE BALANÇO CALÓRICO
        # -----------------------------------------------------------
        peso_atual = ultima_meta.peso_atual if ultima_meta else (user.peso_inicial or 0)

        altura = user.altura or 0
        idade = user.idade or 30
        profissao = user.profissao or "sedentario"

        # Evita calculo inválido
        if peso_atual <= 0 or altura <= 0:
            tmb = 0
        else:
            tmb = calcular_tmb(peso_atual, altura, idade)

        gasto_profissional = calcular_gasto_profissional(tmb, profissao)

        calorias_exercicio = atividade.calorias_perdidas if atividade else 0
        calorias_rotina = sum((r.calorias or 0) for r in rotinas if r.concluido)
        calorias_extras = sum(e.calorias for e in extras)

        total_gasto = tmb + gasto_profissional + calorias_exercicio
        total_consumido = calorias_rotina + calorias_extras

        balanco = total_consumido - total_gasto
        status = "deficit" if balanco < 0 else "superavit"

        # -----------------------------------------------------------
        # RESPOSTA FINAL
        # -----------------------------------------------------------
        return (
            jsonify(
                {
                    "user": user.to_dict(),
                    "meta": ultima_meta.to_dict() if ultima_meta else None,
                    "atividade": atividade.to_dict() if atividade else None,
                    "rotinas": [r.to_dict() for r in rotinas],
                    "calorias_extras": [e.to_dict() for e in extras],
                    "balanco_calorico": {
                        "tmb": tmb,
                        "gasto_profissional": gasto_profissional,
                        "calorias_exercicio": calorias_exercicio,
                        "total_gasto": total_gasto,
                        "calorias_rotina": calorias_rotina,
                        "calorias_extras": calorias_extras,
                        "total_consumido": total_consumido,
                        "balanco": balanco,
                        "status": status,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
