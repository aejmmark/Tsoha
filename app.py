from flask import Flask

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True

from routes.main import main_routes
from routes.new import new_routes
from routes.edit import edit_routes
from routes.users import users_routes

app.register_blueprint(main_routes)
app.register_blueprint(new_routes)
app.register_blueprint(edit_routes)
app.register_blueprint(users_routes)
