from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app import db
from app.models import User, MetaPeso

auth_bp = Blueprint("auth", __name__)


# ----------------------------------------
# Helpers
# ----------------------------------------


def error(message, status=400):
    return jsonify({"error": message}), status


def get_body():
    data = request.get_json(silent=True)
    return data or {}


# ----------------------------------------
# OPTIONS
# ----------------------------------------


@auth_bp.route("/cadastro", methods=["OPTIONS"])
@auth_bp.route("/login", methods=["OPTIONS"])
@auth_bp.route("/refresh", methods=["OPTIONS"])
@auth_bp.route("/ping", methods=["OPTIONS"])
def handle_options():
    return "", 204


# ----------------------------------------
# Cadastro
# ----------------------------------------


@auth_bp.route("/cadastro", methods=["POST"])
def cadastro():
    """
    Cadastrar usuário.
    Campos obrigatórios:
        nome, telefone, senha
    Campos opcionais:
        altura, peso_inicial, profissao, idade, peso_meta
    """
    try:
        data = get_body()

        nome = data.get("nome")
        telefone = data.get("telefone")
        senha = data.get("senha")

        if not nome or not telefone or not senha:
            return error("Nome, telefone e senha são obrigatórios.")

        # Telefone duplicado?
        if User.query.filter_by(telefone=telefone).first():
            return error("Telefone já cadastrado.")

        # Valores opcionais com defaults seguros
        altura = float(data.get("altura") or 1.67)
        peso_inicial = float(data.get("peso_inicial") or 103.0)
        profissao = data.get("profissao") or "Não informado"
        idade = int(data.get("idade") or 18)
        peso_meta = float(data.get("peso_meta") or 85.0)

        # Criar usuário
        user = User(
            nome=nome.strip(),
            telefone=telefone.strip(),
            altura=altura,
            peso_inicial=peso_inicial,
            profissao=profissao,
            idade=idade,
        )
        user.set_password(senha)

        db.session.add(user)
        db.session.commit()

        # Criar meta
        meta = MetaPeso(
            user_id=user.id,
            peso_atual=peso_inicial,
            peso_meta=peso_meta,
        )

        db.session.add(meta)
        db.session.commit()

        # Tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "message": "Usuário cadastrado com sucesso!",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return error(str(e), 500)


# ----------------------------------------
# Login
# ----------------------------------------


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = get_body()

        telefone = data.get("telefone")
        senha = data.get("senha")

        if not telefone or not senha:
            return error("Telefone e senha são obrigatórios.")

        user = User.query.filter_by(telefone=telefone).first()

        if not user or not user.check_password(senha):
            return error("Telefone ou senha incorretos.", 401)

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "message": "Login realizado com sucesso!",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        return error(str(e), 500)


# ----------------------------------------
# Refresh
# ----------------------------------------


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user = str(get_jwt_identity())
        access_token = create_access_token(identity=current_user)

        return jsonify({"access_token": access_token}), 200

    except Exception as e:
        return error(str(e), 500)


# ----------------------------------------
# Ping
# ----------------------------------------


@auth_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "Pong! API Auth funcionando 🔥"}), 200
