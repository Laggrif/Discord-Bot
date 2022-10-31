import os

from discord.ext import commands
from flask import Flask
from flask_restful import Resource, Api

cwd = os.path.dirname(__file__)
print(cwd)

app = Flask(__name__)
api = Api(app)


@app.route("/")
def home():
    return "<h1 style='color:red'>Welcome!<h1>"


class HA(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(HA, '/ha')


class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.system(f'cd {cwd}')
        os.system(f'gunicorn --bind 0.0.0.0:5000 run_api:app')


def setup(bot):
    bot.add_cog(API(bot))
    print('API loaded')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
