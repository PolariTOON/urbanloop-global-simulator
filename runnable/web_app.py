import os

from flask import Flask, render_template

web_directory = os.path.abspath('../resources/web')
app = Flask(__name__, static_folder=web_directory, template_folder=web_directory)


@app.route("/")
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(port=8081)
