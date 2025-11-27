from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User

user_bp = Blueprint("user", __name__)


# ---------------------------
# GET /me  → Dados do usuário
# ---------------------------
@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_user():
    """
    Retorna os dados do usuário autenticado.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado."}), 404

        return jsonify(user.to_dict()), 200

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


# ---------------------------------------------
# PUT /update  → Atualiza dados do perfil
# ---------------------------------------------
@user_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_user():
    """
    Atualiza informações do usuário autenticado.
    Body esperado: altura (float), profissao (str), idade (int)
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado."}), 404

        data = request.get_json() or {}

        # Campos permitidos para atualização
        campos_validos = {
            "altura": float,
            "profissao": str,
            "idade": int,
        }

        # Atualiza apenas o que foi enviado e é válido
        for campo, tipo in campos_validos.items():
            if campo in data:
                try:
                    setattr(user, campo, tipo(data[campo]))
                except (ValueError, TypeError):
                    return jsonify({"error": f"Valor inválido para '{campo}'."}), 400

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Perfil atualizado com sucesso!",
                    "user": user.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
