from flask import Flask

app = Flask(__name__, template_folder="templates/", static_folder="templates/", static_url_path="")

from app import routes
