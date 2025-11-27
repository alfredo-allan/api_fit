from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import CaloriasExtras
from datetime import date

calorias_bp = Blueprint("calorias", __name__)


def json_error(message, status=400):
    """Retorno de erro padronizado."""
    return jsonify({"error": message}), status


def get_user_id():
    """Wrapper para pegar usuário autenticado."""
    return get_jwt_identity()


def hoje():
    """Retorna a data atual (para manter consistência)."""
    return date.today()


@calorias_bp.route("/hoje", methods=["GET"])
@jwt_required()
def get_calorias_extras_hoje():
    """Obter calorias extras do dia atual."""
    try:
        user_id = get_user_id()

        calorias = CaloriasExtras.query.filter_by(user_id=user_id, data=hoje()).all()

        total = sum(c.calorias for c in calorias)

        return (
            jsonify(
                {"calorias_extras": [c.to_dict() for c in calorias], "total": total}
            ),
            200,
        )

    except Exception as e:
        return json_error(str(e), 500)


@calorias_bp.route("/registrar", methods=["POST"])
@jwt_required()
def registrar_calorias_extras():
    """Registrar calorias extras consumidas."""
    try:
        user_id = get_user_id()
        data = request.get_json() or {}

        if "calorias" not in data:
            return json_error("Campo 'calorias' é obrigatório")

        try:
            calorias_valor = int(data["calorias"])
        except ValueError:
            return json_error("O campo 'calorias' deve ser numérico", 400)

        registro = CaloriasExtras(
            user_id=user_id,
            descricao=data.get("descricao", ""),
            calorias=calorias_valor,
            sincero=bool(data.get("sincero", True)),
            data=hoje(),
        )

        db.session.add(registro)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Calorias extras registradas!",
                    "caloria_extra": registro.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return json_error(str(e), 500)


@calorias_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def deletar_caloria_extra(id):
    """Deletar registro de caloria extra."""
    try:
        user_id = get_user_id()

        registro = CaloriasExtras.query.filter_by(id=id, user_id=user_id).first()

        if registro is None:
            return json_error("Registro não encontrado", 404)

        db.session.delete(registro)
        db.session.commit()

        return jsonify({"message": "Registro deletado com sucesso!"}), 200

    except Exception as e:
        db.session.rollback()
        return json_error(str(e), 500)
