from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from sqlalchemy import desc, Column
from app import db
from app.models import AtividadeFisica

atividades_bp = Blueprint("atividades", __name__)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def error(msg, status=400):
    """Resposta de erro padronizada."""
    return jsonify({"error": msg}), status


def get_body():
    """Recupera body JSON com fallback seguro."""
    data = request.get_json(silent=True)
    return data or {}


# Necessário para evitar erro do Pylance com __table__.c.data
def col(c: Column):
    """Garantir tipagem correta para operações SQL."""
    return c


# ---------------------------------------------------------
# GET /hoje — Obter atividade do dia
# ---------------------------------------------------------
@atividades_bp.route("/hoje", methods=["GET"])
@jwt_required()
def get_atividade_hoje():
    """
    Retorna a atividade física registrada no dia atual.
    Se não existir, retorna estrutura zerada.
    """
    try:
        user_id = get_jwt_identity()
        hoje = date.today()

        atividade = AtividadeFisica.query.filter_by(user_id=user_id, data=hoje).first()

        if not atividade:
            vazio = {
                "km_percorridos": 0,
                "calorias_perdidas": 0,
                "calorias_trabalho": 0,
            }

            return (
                jsonify(
                    {
                        "message": "Nenhuma atividade registrada hoje",
                        "atividade": vazio,
                    }
                ),
                200,
            )

        return jsonify(atividade.to_dict()), 200

    except Exception as e:
        return error(str(e), 500)


# ---------------------------------------------------------
# POST /registrar — Criar ou atualizar atividade do dia
# ---------------------------------------------------------
@atividades_bp.route("/registrar", methods=["POST"])
@jwt_required()
def registrar_atividade():
    """
    Registrar ou atualizar atividade física do dia.
    Campos permitidos:
      - km_percorridos
      - calorias_perdidas
      - calorias_trabalho
    """
    try:
        user_id = get_jwt_identity()
        body = get_body()
        hoje = date.today()

        atividade = AtividadeFisica.query.filter_by(user_id=user_id, data=hoje).first()

        if not atividade:
            atividade = AtividadeFisica(user_id=user_id)

        # Atualizar apenas os campos enviados
        if "km_percorridos" in body:
            atividade.km_percorridos = float(body["km_percorridos"])

        if "calorias_perdidas" in body:
            atividade.calorias_perdidas = int(body["calorias_perdidas"])

        if "calorias_trabalho" in body:
            atividade.calorias_trabalho = int(body["calorias_trabalho"])

        db.session.add(atividade)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Atividade registrada com sucesso!",
                    "atividade": atividade.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return error(str(e), 500)


# ---------------------------------------------------------
# GET /historico — últimos 30 dias
# ---------------------------------------------------------
@atividades_bp.route("/historico", methods=["GET"])
@jwt_required()
def get_historico_atividades():
    """
    Obter histórico de atividades dos últimos 30 dias.
    """
    try:
        user_id = get_jwt_identity()

        atividades = (
            AtividadeFisica.query.filter_by(user_id=user_id)
            .order_by(desc(col(AtividadeFisica.data)))
            .limit(30)
            .all()
        )

        return jsonify([a.to_dict() for a in atividades]), 200

    except Exception as e:
        return error(str(e), 500)
