from flask import Flask, redirect, render_template, request, url_for
import requests


app = Flask(__name__)

dev = False
api_url = "http://localhost:3001" if dev else "https://api.sercraft.ch"


@app.get("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            response = requests.post(
                api_url + "/login",
                json={"username": username, "password": password},
            )
            error_message = response.json().get("message", response.text)
            return render_template(
                "login.html", error=error_message, password=password, username=username
            )

        except requests.exceptions.ConnectionError:
            return render_template(
                "login.html",
                error="Kein verbundg mit der API",
                password=password,
                username=username,
            )
        except Exception as e:
            print(type(e))
            print(e)
            return render_template(
                "login.html", error=e, password=password, username=username
            )
    else:
        return render_template(
            "login.html",
        )


def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
