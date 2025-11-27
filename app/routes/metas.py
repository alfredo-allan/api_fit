from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import MetaPeso

metas_bp = Blueprint("metas", __name__)


# -------------------------------------------------------
# GET /  → Todas as metas do usuário (ordenadas por data)
# -------------------------------------------------------
@metas_bp.route("/", methods=["GET"])
@jwt_required()
def get_metas():
    try:
        user_id = get_jwt_identity()

        metas = (
            MetaPeso.query.filter_by(user_id=user_id)
            .order_by(MetaPeso.data_registro.desc())
            .all()
        )

        return jsonify([m.to_dict() for m in metas]), 200

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


# -------------------------------------------------------
# GET /ultima  → Última meta registrada
# -------------------------------------------------------
@metas_bp.route("/ultima", methods=["GET"])
@jwt_required()
def get_ultima_meta():
    try:
        user_id = get_jwt_identity()

        meta = (
            MetaPeso.query.filter_by(user_id=user_id)
            .order_by(MetaPeso.data_registro.desc())
            .first()
        )

        if not meta:
            return jsonify({"error": "Nenhuma meta encontrada."}), 404

        return jsonify(meta.to_dict()), 200

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


# -------------------------------------------------------
# POST /criar  → Criar nova meta de peso
# -------------------------------------------------------
@metas_bp.route("/criar", methods=["POST"])
@jwt_required()
def criar_meta():
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        # Validação forte
        if "peso_atual" not in data:
            return jsonify({"error": "O campo 'peso_atual' é obrigatório."}), 400

        try:
            peso_atual = float(data["peso_atual"])
        except (ValueError, TypeError):
            return jsonify({"error": "Valor inválido para peso_atual."}), 400

        try:
            peso_meta = float(data.get("peso_meta", 85.0))
        except (ValueError, TypeError):
            return jsonify({"error": "Valor inválido para peso_meta."}), 400

        meta = MetaPeso(
            user_id=user_id,
            peso_atual=peso_atual,
            peso_meta=peso_meta,
        )

        db.session.add(meta)
        db.session.commit()

        return (
            jsonify({"message": "Meta criada com sucesso!", "meta": meta.to_dict()}),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


# ---------------------------------------------------------------------
# GET /historico  → Histórico completo formatado para gráficos
# ---------------------------------------------------------------------
@metas_bp.route("/historico", methods=["GET"])
@jwt_required()
def historico_peso():
    try:
        user_id = get_jwt_identity()
        metas = (
            MetaPeso.query.filter_by(user_id=user_id)
            .order_by(MetaPeso.data_registro.asc())
            .all()
        )

        historico = [
            {
                "data": m.data_registro.strftime("%d/%m/%Y"),
                "peso": m.peso_atual,
                "meta": m.peso_meta,
            }
            for m in metas
        ]

        return jsonify(historico), 200

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
