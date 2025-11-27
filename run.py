from app import create_app, db
from app.models import (
    User,
    MetaPeso,
    RotinaAlimentar,
    AtividadeFisica,
    CaloriasExtras,
    ConsumoCalorico,
)

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "MetaPeso": MetaPeso,
        "RotinaAlimentar": RotinaAlimentar,
        "AtividadeFisica": AtividadeFisica,
        "CaloriasExtras": CaloriasExtras,
        "ConsumoCalorico": ConsumoCalorico,
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    # Configurações para evitar problemas de CORS
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
