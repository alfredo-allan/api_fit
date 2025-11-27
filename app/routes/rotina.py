from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import RotinaAlimentar
from app.utils import calcular_calorias_refeicao
from datetime import date

rotina_bp = Blueprint("rotina", __name__)


# ---------------------------------------------------
# GET /hoje  → Retorna rotina alimentar do dia
# ---------------------------------------------------
@rotina_bp.route("/hoje", methods=["GET"])
@jwt_required()
def get_rotina_hoje():
    try:
        user_id = get_jwt_identity()
        hoje = date.today()

        rotinas = RotinaAlimentar.query.filter_by(user_id=user_id, data=hoje).all()

        # Se não tem rotinas para hoje, cria as padrão
        if not rotinas:
            rotinas = criar_rotina_padrao_hoje(user_id)

        return jsonify([r.to_dict() for r in rotinas]), 200

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


def criar_rotina_padrao_hoje(user_id):
    """Cria rotina padrão para o dia atual"""
    periodos = [
        ("Café da Manhã", "Café da Manhã"),
        ("Almoço", "Almoço"),
        ("Lanche da Tarde", "Lanche da Tarde"),
        ("Janta", "Janta"),
        ("Ceia", "Ceia"),
    ]

    rotinas = []
    for periodo, refeicao in periodos:
        rotina = RotinaAlimentar(
            user_id=user_id, periodo=periodo, refeicao=refeicao, concluido=False
        )
        db.session.add(rotina)
        rotinas.append(rotina)

    db.session.commit()
    return rotinas


# --------------------------------------------------------
# POST /marcar  → Atualiza / cria refeição do dia
# --------------------------------------------------------
@rotina_bp.route("/marcar", methods=["POST"])
@jwt_required()
def marcar_refeicao():
    try:
        user_id = get_jwt_identity()
        hoje = date.today()
        data = request.get_json() or {}

        periodo = data.get("periodo")
        proteina = data.get("proteina_selecionada")
        concluido = bool(data.get("concluido", False))

        if not periodo:
            return jsonify({"error": "O campo 'periodo' é obrigatório."}), 400

        # Buscar rotina existente
        rotina = RotinaAlimentar.query.filter_by(
            user_id=user_id, periodo=periodo, data=hoje
        ).first()

        # Se não existir → cria CORRETAMENTE
        if not rotina:
            rotina = RotinaAlimentar(
                user_id=user_id,
                periodo=periodo,
                refeicao=periodo,
                proteina_selecionada=proteina,  # ✅ CORRETO
                concluido=concluido,
                # data é preenchida automaticamente
            )
            db.session.add(rotina)
        else:
            # Atualizações
            rotina.proteina_selecionada = proteina
            rotina.concluido = concluido

        # Calcula calorias
        rotina.calorias = calcular_calorias_refeicao(periodo, proteina)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Refeição atualizada com sucesso!",
                    "rotina": rotina.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


# --------------------------------------------------------------------
# GET /calorias-totais  → Soma calorias consumidas nas refeições concluídas
# --------------------------------------------------------------------


@rotina_bp.route("/calorias-totais", methods=["GET"])
@jwt_required()
def get_calorias_totais():
    try:
        user_id = get_jwt_identity()
        hoje = date.today()

        rotinas = RotinaAlimentar.query.filter_by(user_id=user_id, data=hoje).all()

        concluidas = [r for r in rotinas if r.concluido]
        total_calorias = sum((r.calorias or 0) for r in concluidas)

        return (
            jsonify(
                {
                    "total_calorias": total_calorias,
                    "refeicoes_concluidas": len(concluidas),
                    "total_refeicoes": len(rotinas),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
