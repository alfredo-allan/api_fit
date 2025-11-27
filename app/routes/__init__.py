from flask import Blueprint

def register_blueprints(app):
    """
    Registra todos os blueprints da aplicação
    """
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.metas import metas_bp
    from app.routes.rotina import rotina_bp
    from app.routes.atividades import atividades_bp
    from app.routes.calorias import calorias_bp
    from app.routes.calculos import calculos_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(metas_bp, url_prefix='/api/metas')
    app.register_blueprint(rotina_bp, url_prefix='/api/rotina')
    app.register_blueprint(atividades_bp, url_prefix='/api/atividades')
    app.register_blueprint(calorias_bp, url_prefix='/api/calorias-extras')
    app.register_blueprint(calculos_bp, url_prefix='/api/calculos')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')