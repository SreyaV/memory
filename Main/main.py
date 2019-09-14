from flask import Flask, render_template, url_for
import os

app = Flask(__name__)

# 
#########
# Links #
#########
@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)
