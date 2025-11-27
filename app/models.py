from datetime import datetime, date
from typing import Optional, Dict, Any

from app import db
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================
# USER MODEL
# ============================================================


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    altura = db.Column(db.Float, nullable=True)
    peso_inicial = db.Column(db.Float, nullable=True)
    profissao = db.Column(db.String(100), nullable=True)
    idade = db.Column(db.Integer, default=30)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    metas = db.relationship(
        "MetaPeso",
        backref="usuario",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    rotinas = db.relationship(
        "RotinaAlimentar",
        backref="usuario",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    atividades = db.relationship(
        "AtividadeFisica",
        backref="usuario",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    calorias_extras = db.relationship(
        "CaloriasExtras",
        backref="usuario",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    consumo_calorico = db.relationship(
        "ConsumoCalorico",
        backref="usuario",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # --------------------------------------------------------

    def __init__(
        self,
        nome: str,
        telefone: str,
        altura: Optional[float] = None,
        peso_inicial: Optional[float] = None,
        profissao: Optional[str] = None,
        idade: int = 30,
    ):
        self.nome = nome
        self.telefone = telefone
        self.altura = altura
        self.peso_inicial = peso_inicial
        self.profissao = profissao
        self.idade = idade

    # --------------------------------------------------------

    def set_password(self, password: str) -> None:
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.senha_hash, password)

    def calcular_imc(self) -> Optional[float]:
        if not self.altura or not self.peso_inicial:
            return None
        try:
            return round(self.peso_inicial / (self.altura**2), 1)
        except ZeroDivisionError:
            return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "altura": self.altura,
            "peso_inicial": self.peso_inicial,
            "profissao": self.profissao,
            "idade": self.idade,
            "imc": self.calcular_imc(),
            "data_cadastro": (
                self.data_cadastro.isoformat() if self.data_cadastro else None
            ),
        }


# ============================================================
# META PESO
# ============================================================


class MetaPeso(db.Model):
    __tablename__ = "metas_peso"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    peso_atual = db.Column(db.Float, nullable=False)
    peso_meta = db.Column(db.Float, nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id: int, peso_atual: float, peso_meta: float):
        self.user_id = user_id
        self.peso_atual = peso_atual
        self.peso_meta = peso_meta

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "peso_atual": self.peso_atual,
            "peso_meta": self.peso_meta,
            "falta_perder": round(self.peso_atual - self.peso_meta, 1),
            "data_registro": self.data_registro.isoformat(),
        }


# ============================================================
# ROTINA ALIMENTAR
# ============================================================


class RotinaAlimentar(db.Model):
    __tablename__ = "rotina_alimentar"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    periodo = db.Column(db.String(50), nullable=False)
    refeicao = db.Column(db.String(200), nullable=False)
    proteina_selecionada = db.Column(db.String(100), nullable=True)
    gramas_proteina = db.Column(db.Integer, nullable=True)
    calorias = db.Column(db.Integer, nullable=True)
    concluido = db.Column(db.Boolean, default=False)
    data = db.Column(db.Date, default=date.today)

    # Relacionamento
    user = db.relationship("User", backref="rotinas_alimentares")

    def __init__(
        self,
        user_id: int,
        periodo: str,
        refeicao: str,
        proteina_selecionada: Optional[str] = None,
        gramas_proteina: Optional[int] = None,
        calorias: Optional[int] = None,
        concluido: bool = False,
        data=None,  # ✅ PARÂMETRO ADICIONADO
    ):
        self.user_id = user_id
        self.periodo = periodo
        self.refeicao = refeicao
        self.proteina_selecionada = proteina_selecionada
        self.gramas_proteina = gramas_proteina
        self.calorias = calorias
        self.concluido = concluido
        self.data = data or date.today()  # ✅ CORRIGIDO

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "periodo": self.periodo,
            "refeicao": self.refeicao,
            "proteina_selecionada": self.proteina_selecionada,
            "gramas_proteina": self.gramas_proteina,
            "calorias": self.calorias,
            "concluido": self.concluido,
            "data": self.data.isoformat(),
        }


# ============================================================
# ATIVIDADE FÍSICA
# ============================================================


class AtividadeFisica(db.Model):
    __tablename__ = "atividades_fisicas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    km_percorridos = db.Column(db.Float, default=0.0)
    calorias_perdidas = db.Column(db.Integer, default=0)
    calorias_trabalho = db.Column(db.Integer, default=0)
    data = db.Column(db.Date, default=date.today, nullable=False)

    def __init__(
        self,
        user_id: int,
        km_percorridos: float = 0.0,
        calorias_perdidas: int = 0,
        calorias_trabalho: int = 0,
        data: Optional[date] = None,
    ):
        self.user_id = user_id
        self.km_percorridos = km_percorridos
        self.calorias_perdidas = calorias_perdidas
        self.calorias_trabalho = calorias_trabalho
        self.data = data or date.today()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "km_percorridos": self.km_percorridos,
            "calorias_perdidas": self.calorias_perdidas,
            "calorias_trabalho": self.calorias_trabalho,
            "data": self.data.isoformat(),
        }


# ============================================================
# CALORIAS EXTRAS
# ============================================================


class CaloriasExtras(db.Model):
    __tablename__ = "calorias_extras"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    descricao = db.Column(db.String(200), nullable=True)
    calorias = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Date, default=date.today)
    sincero = db.Column(db.Boolean, default=True)

    def __init__(
        self,
        user_id: int,
        descricao: Optional[str],
        calorias: int,
        sincero: bool = True,
        data: Optional[date] = None,
    ):
        self.user_id = user_id
        self.descricao = descricao
        self.calorias = calorias
        self.sincero = sincero
        self.data = data or date.today()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "descricao": self.descricao,
            "calorias": self.calorias,
            "data": self.data.isoformat(),
            "sincero": self.sincero,
        }


# ============================================================
# CONSUMO CALÓRICO
# ============================================================


class ConsumoCalorico(db.Model):
    __tablename__ = "consumo_calorico"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    calorias_consumidas = db.Column(db.Integer, default=0, nullable=False)
    calorias_gastas = db.Column(db.Integer, default=0, nullable=False)
    metabolismo_basal = db.Column(db.Integer, default=0, nullable=False)
    gasto_profissional = db.Column(db.Integer, default=0, nullable=False)

    data = db.Column(db.Date, nullable=False, default=date.today)

    def __init__(
        self,
        user_id: int,
        data: Optional[date] = None,
        calorias_consumidas: int = 0,
        calorias_gastas: int = 0,
        metabolismo_basal: int = 0,
        gasto_profissional: int = 0,
    ):
        self.user_id = user_id
        self.data = data or date.today()
        self.calorias_consumidas = calorias_consumidas
        self.calorias_gastas = calorias_gastas
        self.metabolismo_basal = metabolismo_basal
        self.gasto_profissional = gasto_profissional

    def balanco_calorico(self) -> int:
        return self.calorias_consumidas - self.calorias_gastas

    def to_dict(self):
        return {
            "id": self.id,
            "calorias_consumidas": self.calorias_consumidas,
            "calorias_gastas": self.calorias_gastas,
            "metabolismo_basal": self.metabolismo_basal,
            "gasto_profissional": self.gasto_profissional,
            "balanco": self.balanco_calorico(),
            "data": self.data.isoformat(),
        }
