import os

from flask import Flask, redirect, render_template, request, url_for, session
import requests


app = Flask(__name__)

dev_url = False
api_url = "http://localhost:3001" if dev_url else "https://api.sercraft.ch"
dev = True
app.config["SESSION_COOKIE_SECURE"] = not dev
app.config["SESSION_COOKIE_HTTPONLY"] = not dev
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.secret_key = "jakljlkfjklfhfajljhoaifpoafjhioh" if dev else os.urandom(24)


@app.get("/")
def index():
    token = session.get("access_token")
    print(token)
    if token is not None:
        headers = {"x-access-token": f"{token}"}
        print(headers)
        response = requests.get(api_url + "/user", headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            username = response_json["user"]["username"]
            session["username"] = username
            response = requests.get(api_url + "/user", headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                print(response_json)
                total_average = response_json["user"]["total_average"]
                total_exams = response_json["user"]["total_exams"]
                total_points = response_json["user"]["total_points"]
                print(total_average, total_exams, total_points)
                return render_template(
                    "loggedin.html",
                    username=username,
                    total_avrage=total_average,
                    total_exams=total_exams,
                    total_points=total_points,
                )
            return render_template("loggedin.html", username=username)

        else:
            return render_template("index.html", error="Error")

    else:
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    token = session.get("access_token")
    if token is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            response = requests.post(
                api_url + "/login",
                json={"username": username, "password": password},
            )
            response_json = response.json()
            if response_json["success"]:
                session["access_token"] = response_json["token"]
                return redirect(url_for("index"))
            else:
                error_message = response_json["message"]

            return render_template(
                "login.html",
                message=error_message,
                password=password,
                username=username,
                error=True,
            )

        except requests.exceptions.ConnectionError:
            return render_template(
                "login.html",
                message="Kein verbundg mit der API",
                password=password,
                username=username,
                error=True,
            )
        except Exception as e:
            print(type(e))
            print(e)
            return render_template(
                "login.html",
                message=e,
                password=password,
                username=username,
                error=True,
            )
    else:
        return render_template(
            "login.html",
            error=False,
        )

@app.route("/register", methods=["GET", "POST"])
def register():
    token = session.get("access_token")
    if token is not None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            return render_template(
                "register.html",
                error=True,
                message="Bitte geben Sie einen Benutzernamen und ein Passwort ein.",
            )
        try:
            response = requests.post(
                url=api_url + "/register",
                json={"username": username, "password": password},
            )
            response_json = response.json()
            print(response_json)
            if response_json["success"]:
                session["access_token"] = response_json["token"]
                return redirect(url_for("index"))
            else:
                return render_template(
                    "register.html",
                    error=True,
                    message=response_json["message"],
                    username=username,
                    password=password,
                )

        except Exception as e:
            print(e)
            return render_template(
                "register.html",
                error=True,
                message=e,
                username=username,
                password=password,
            )
    return render_template("register.html", error=False)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/delete")
def delete():
    token = session.get("access_token")
    if token is not None:
        headers = {"x-access-token": f"{token}"}
        response = requests.delete(api_url + "/user", headers=headers)
        if response.status_code == 200:
            session.clear()
            return redirect(url_for("index"))
        else:
            return render_template("index.html", error="Error")
    else:
        return redirect(url_for("login"))

def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run(debug=True)
