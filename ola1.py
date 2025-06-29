from flask import Flask, render_template, request, redirect, url_for

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

if __name__ == "__main__":
    app.run(debug=True)
