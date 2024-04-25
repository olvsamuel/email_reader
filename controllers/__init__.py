from .email_reader import email_reader_bp

def register_blueprints(app):
    app.register_blueprint(email_reader_bp, url_prefix='/api')