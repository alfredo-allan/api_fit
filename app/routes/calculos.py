# app/routes/calculos.py
from datetime import date
from typing import Tuple, Optional

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import (
    User,
    MetaPeso,
    AtividadeFisica,
    RotinaAlimentar,
    CaloriasExtras,
    ConsumoCalorico,
)
from app.utils import calcular_tmb, calcular_gasto_profissional

calculos_bp = Blueprint("calculos", __name__)


# -------------------------------
# Helpers
# -------------------------------


def json_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def hoje() -> date:
    return date.today()


def get_user_or_404(
    user_id: int,
) -> Tuple[Optional[User], Optional[Tuple]]:  # (user, error_response)
    user = User.query.get(user_id)
    if not user:
        return None, json_error("Usuário não encontrado", 404)
    return user, None


def get_peso_atual(user_id: int, user: User) -> float:
    """
    Retorna o peso atual a partir da última meta, ou peso inicial do usuário.
    Garante que sempre retorne um float (ou 0.0 como fallback).
    """
    ultima_meta = (
        MetaPeso.query.filter_by(user_id=user_id)
        .order_by(MetaPeso.data_registro.desc())
        .first()
    )

    peso = (ultima_meta.peso_atual if ultima_meta else user.peso_inicial) or 0.0
    try:
        return float(peso)
    except (TypeError, ValueError):
        return 0.0


def calcular_basais(user: User, peso: float) -> Tuple[float, float]:
    """
    Calcula TMB e gasto profissional com proteção contra entradas inválidas.
    """
    if not peso or not user.altura:
        return 0.0, 0.0

    try:
        tmb = calcular_tmb(peso, user.altura, user.idade or 30)
    except Exception:
        tmb = 0.0

    try:
        gasto_prof = calcular_gasto_profissional(tmb, user.profissao or "")
    except Exception:
        gasto_prof = 0.0

    return tmb or 0.0, gasto_prof or 0.0


# -------------------------------
# Rotas
# -------------------------------


@calculos_bp.route("/tmb", methods=["GET"])
@jwt_required()
def calcular_tmb_user():
    """Calcular a Taxa Metabólica Basal do usuário."""
    try:
        user_id = get_jwt_identity()

        user, err = get_user_or_404(user_id)
        if err:
            return err

        peso = get_peso_atual(user_id, user)
        tmb, gasto_prof = calcular_basais(user, peso)

        return (
            jsonify(
                {
                    "tmb": tmb,
                    "gasto_profissional": gasto_prof,
                    "total_gasto_basal": tmb + gasto_prof,
                }
            ),
            200,
        )

    except Exception as e:
        return json_error(f"Erro interno: {str(e)}", 500)


@calculos_bp.route("/balanco-calorico", methods=["GET"])
@jwt_required()
def calcular_balanco_calorico():
    """Calcular balanço calórico completo do dia e persistir em ConsumoCalorico."""
    try:
        user_id = get_jwt_identity()
        data_atual = hoje()

        user, err = get_user_or_404(user_id)
        if err:
            return err

        # Basais
        peso = get_peso_atual(user_id, user)
        tmb, gasto_prof = calcular_basais(user, peso)

        # Atividade física do dia
        atividade = AtividadeFisica.query.filter_by(
            user_id=user_id, data=data_atual
        ).first()
        calorias_exercicio = atividade.calorias_perdidas if atividade else 0

        # Rotina alimentar (somente concluídas)
        rotinas = RotinaAlimentar.query.filter_by(
            user_id=user_id, data=data_atual
        ).all()
        calorias_rotina = sum((r.calorias or 0) for r in rotinas if r.concluido)

        # Calorias extras
        extras = CaloriasExtras.query.filter_by(user_id=user_id, data=data_atual).all()
        calorias_extras = sum((e.calorias or 0) for e in extras)

        # Cálculos finais
        total_gasto = tmb + gasto_prof + (calorias_exercicio or 0)
        total_consumido = calorias_rotina + calorias_extras
        balanco = total_consumido - total_gasto
        status = "deficit" if balanco < 0 else "superavit"

        # Persistência em ConsumoCalorico
        # Observação: o modelo ConsumoCalorico original exige determinados parâmetros no __init__.
        # Para evitar mismatch com o construtor atual, criamos/atualizamos a instância via atribuições.
        consumo = ConsumoCalorico.query.filter_by(
            user_id=user_id, data=data_atual
        ).first()

        if not consumo:
            # Se o seu modelo não aceita 'data' no __init__, instancia com valores mínimos
            # e atribui data abaixo. Isso evita erro de "argumento inesperado".
            consumo = ConsumoCalorico(
                user_id=user_id,
                calorias_consumidas=int(total_consumido),
                calorias_gastas=int(total_gasto),
                metabolismo_basal=int(tmb),
                gasto_profissional=int(gasto_prof),
            )
            # setar data explicitamente (caso o construtor não aceite)
            consumo.data = data_atual
            db.session.add(consumo)
        else:
            consumo.metabolismo_basal = int(tmb)
            consumo.gasto_profissional = int(gasto_prof)
            consumo.calorias_gastas = int(total_gasto)
            consumo.calorias_consumidas = int(total_consumido)
            consumo.data = data_atual

        db.session.commit()

        return (
            jsonify(
                {
                    "metabolismo_basal": tmb,
                    "gasto_profissional": gasto_prof,
                    "calorias_exercicio": calorias_exercicio,
                    "total_gasto": total_gasto,
                    "calorias_rotina": calorias_rotina,
                    "calorias_extras": calorias_extras,
                    "total_consumido": total_consumido,
                    "balanco": balanco,
                    "status": status,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return json_error(f"Erro interno: {str(e)}", 500)
