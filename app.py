from flask import Flask
from dotenv import load_dotenv
from controllers import register_blueprints

load_dotenv()

app = Flask(__name__)

register_blueprints(app)

if __name__ == '__main__':
    app.run(port=6010)
