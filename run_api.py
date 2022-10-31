from waitress import serve
import cogs.API as API

if __name__ == "__main__":
    serve(API.app, host='127.0.0.1', port=5000)
