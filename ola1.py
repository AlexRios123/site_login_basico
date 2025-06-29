from flask import Flask, render_template, request, redirect, url_for
import os
app = Flask(__name__)

USUARIO = "alex"
SENHA = "123"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == USUARIO and senha == SENHA:
            return redirect(url_for("bemvindo"))
        else:
            return render_template("login.html", erro="Usuário ou senha incorretos.")
    return render_template("login.html")

@app.route("/bemvindo")
def bemvindo():
    return render_template("bemvindo.html")





@app.route("/nutricao", methods=["POST"])
def login_nutri():
    usuario = request.form["usuario"]
    senha = request.form["senha"]
    if usuario == "adm" and senha == "123":
        return render_template("nutricao.html")
    else:
        return render_template("bemvindo.html", erro_nutri="Usuário ou senha inválidos")

@app.route("/psicologia", methods=["POST"])
def login_psico():
    usuario = request.form["usuario"]
    senha = request.form["senha"]
    if usuario == "adm" and senha == "123":
        return "Área da Psicologia"
    else:
        return render_template("bemvindo.html", erro_psico="Usuário ou senha inválidos")








if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)