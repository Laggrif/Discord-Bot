import os
import threading

from discord.ext import commands
from flask import Flask, request
from turbo_flask import Turbo
from flask_restful import Resource, Api

cwd = os.path.dirname(__file__)
print(cwd)

app = Flask(__name__)
api = Api(app)

to = {}


@app.route("/")
def home():
    return f"<h1 style='color:red'>{to}<h1>"


class HA(Resource):
    def __init__(self):
        global to
        self.to = to

    def get(self, id):
        return self.to[id]

    def put(self, id):
        self.to[id] = str(request.form['data'])
        return self.to


api.add_resource(HA, '/gp<string:id>')


class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # os.system(f'cd {cwd}')
        # os.system(f'gunicorn --bind 0.0.0.0:5000 run_api:app')


def setup(bot):
    bot.add_cog(API(bot))
    print('API loaded')


"""
if __name__ == "__main__":
    app.run(host='0.0.0.0')
"""