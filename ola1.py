from flask import Flask, render_template, request, redirect, url_for, session

from functools import wraps

import os
import sqlite3
import json
import holidays
from datetime import datetime, timedelta, date
from datetime import datetime as dt
 
 
 
 
 
app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_segura'  # Troque por uma string segura
# Configurações
USUARIO = "alex"
SENHA = "123"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "agenda_nutri.db")

# Banco de dados






def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function











def atualizar_banco_agendamentos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verifica e adiciona coluna plano_nome se necessário
    cursor.execute("PRAGMA table_info(agendamentos_pendentes)")
    colunas = [c[1] for c in cursor.fetchall()]
    if "plano_nome" not in colunas:
        cursor.execute("ALTER TABLE agendamentos_pendentes ADD COLUMN plano_nome TEXT")
    if "tipo_atendimento" not in colunas:
        cursor.execute("ALTER TABLE agendamentos_pendentes ADD COLUMN tipo_atendimento TEXT")

    # Repete para tabela de confirmados
    cursor.execute("PRAGMA table_info(agendamentos_confirmados)")
    colunas = [c[1] for c in cursor.fetchall()]
    if "plano_nome" not in colunas:
        cursor.execute("ALTER TABLE agendamentos_confirmados ADD COLUMN plano_nome TEXT")
    if "tipo_atendimento" not in colunas:
        cursor.execute("ALTER TABLE agendamentos_confirmados ADD COLUMN tipo_atendimento TEXT")

    conn.commit()
    conn.close()





def criar_banco():
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agenda_nutricionista (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia TEXT,
                manha TEXT,
                tarde TEXT,
                noite TEXT,
                excluir_feriados BOOLEAN,
                excluir_sabado BOOLEAN,
                excluir_domingo BOOLEAN,
                duracao_consulta INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agendamentos_pendentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT, cpf TEXT, telefone TEXT,
                data TEXT, hora TEXT,
                plano_nome TEXT,
                tipo_atendimento TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agendamentos_confirmados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT, cpf TEXT, telefone TEXT,
                data TEXT, hora TEXT,
                plano_nome TEXT,
                tipo_atendimento TEXT
            )
        """)
        conn.commit()


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planos_nutricionais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                descricao TEXT,
                valor TEXT
            )
        """)



        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ferias_nutricionista (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_inicio TEXT,
                data_fim TEXT
            )
        """)






criar_banco()
atualizar_banco_agendamentos()
# Rotas
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("usuario") == USUARIO and request.form.get("senha") == SENHA:
            session['logado'] = True
            return redirect(url_for("bemvindo"))
        return render_template("login.html", erro="Usuário ou senha incorretos.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))





@app.route("/bemvindo")
@login_requerido
def bemvindo():
    return render_template("bemvindo.html")

@app.route("/nutricao", methods=["POST", "GET"])
def login_nutri():
    if request.method == "POST":
        if request.form["usuario"] == "adm" and request.form["senha"] == "123":
            return redirect(url_for("nutricao_painel"))
        return render_template("bemvindo.html", erro_nutri="Usuário ou senha inválidos")
    return redirect(url_for("nutricao_painel"))

@app.route("/psicologia", methods=["POST"])
def login_psico():
    if request.form["usuario"] == "adm" and request.form["senha"] == "123":
        return "Área da Psicologia"
    return render_template("bemvindo.html", erro_psico="Usuário ou senha inválidos")

@app.route("/agenda")
@login_requerido
def agenda_nutri():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agenda_nutricionista")
    registros = cursor.fetchall()
    
    # Carrega planos nutricionais (NOVO)
    cursor.execute("SELECT * FROM planos_nutricionais ORDER BY id DESC")
    planos = cursor.fetchall()
    cursor.execute("SELECT * FROM ferias_nutricionista ORDER BY data_inicio")
    ferias = cursor.fetchall()
    
    
    
    
    conn.close()

    dados = {}
    excluir_feriados = excluir_sabado = excluir_domingo = False
    duracao = 30

    for linha in registros:
        dia = linha[1]
        dados[dia] = {
            "manha": linha[2],
            "tarde": linha[3],
            "noite": linha[4]
        }
        excluir_feriados = linha[5]
        excluir_sabado = linha[6]
        excluir_domingo = linha[7]
        duracao = linha[8]

    return render_template("agenda.html", dados=dados,
                           excluir_feriados=excluir_feriados,
                           excluir_sabado=excluir_sabado,
                           excluir_domingo=excluir_domingo,
                           duracao=duracao,
                           
                           planos=planos,
                           ferias=ferias)
                           

@app.route("/salvar_agenda", methods=["POST"])
@login_requerido
def salvar_agenda():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtém lista de dias marcados
    dias = request.form.getlist("dias")
    print("Dias marcados:", dias)

    duracao = int(request.form.get("duracao"))
    excluir_feriados = bool(request.form.get("excluir_feriados"))
    excluir_sabado = False
    excluir_domingo = False

    # Apaga agenda antiga
    cursor.execute("DELETE FROM agenda_nutricionista")

    prefixos = {
        "segunda": "seg",
        "terca": "ter",
        "quarta": "qua",
        "quinta": "qui",
        "sexta": "sex"
    }

    for dia in dias:
        prefixo = prefixos.get(dia)
        if not prefixo:
            print(f"[AVISO] Dia inválido ignorado: {dia}")
            continue

        manha = request.form.get(f"manha_{prefixo}", "").strip()
        tarde = request.form.get(f"tarde_{prefixo}", "").strip()
        noite = request.form.get(f"noite_{prefixo}", "").strip()

        print(f"[{dia}] manha={manha}, tarde={tarde}, noite={noite}")

        cursor.execute("""
            INSERT INTO agenda_nutricionista (
                dia, manha, tarde, noite,
                excluir_feriados, excluir_sabado, excluir_domingo,
                duracao_consulta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (dia, manha, tarde, noite,
              excluir_feriados, excluir_sabado, excluir_domingo, duracao))

    conn.commit()
    conn.close()

    return redirect(url_for("nutricao_painel"))




@app.route("/nutricao_painel")
def nutricao_painel():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos_pendentes WHERE datetime(data || ' ' || hora) < datetime('now', '-1 day')")
    cursor.execute("SELECT * FROM agendamentos_pendentes ORDER BY data, hora")
    pendentes = cursor.fetchall()
    cursor.execute("SELECT * FROM agendamentos_confirmados ORDER BY data, hora")
    confirmados = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template("nutricao.html", pendentes=pendentes, confirmados=confirmados)

@app.route("/confirmar_agendamento", methods=["POST"])

@login_requerido
def confirmar_agendamento():
    id_ = request.form.get("id")
    if not id_:
        return redirect(url_for("nutricao_painel"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agendamentos_pendentes WHERE id=?", (id_,))
    agendamento = cursor.fetchone()

    if agendamento:
        cursor.execute("""
            INSERT INTO agendamentos_confirmados (nome, cpf, telefone, data, hora, plano_nome, tipo_atendimento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, agendamento[1:])  # copia todos os campos menos o ID
            
        
        
        
        
        
        
        cursor.execute("DELETE FROM agendamentos_pendentes WHERE id=?", (id_,))
        conn.commit()
    conn.close()

    return redirect(url_for("nutricao_painel"))





































from flask import Flask, render_template, request, redirect, url_for
import sqlite3, json, holidays
from datetime import datetime, timedelta, date

@app.route("/agendar", methods=["GET", "POST"])
def agendar():
    # 1) Calcula mínimo de 48h e máximo de 20 dias à frente
    agora     = datetime.now()
    daqui_48h = agora + timedelta(hours=48)
    daqui_20d = agora + timedelta(days=20)
    data_minima = daqui_48h.date().isoformat()
    data_maxima = daqui_20d.date().isoformat()


    
    
    
    # Carrega períodos de férias
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data_inicio, data_fim FROM ferias_nutricionista")
    periodos_ferias = cursor.fetchall()
    conn.close()






    # 2) Carrega agenda e duração do banco
    def carregar_agenda():
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agenda_nutricionista")
        linhas = cursor.fetchall()
        conn.close()
        agenda  = {}
        duracao = 30
        for linha in linhas:
            agenda[linha[1]] = {
                "manha": linha[2],
                "tarde": linha[3],
                "noite": linha[4]
            }
            duracao = linha[8]
        return agenda, duracao

    agenda, duracao = carregar_agenda()
    
    
    # Carrega planos do banco
    def carregar_planos():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao, valor FROM planos_nutricionais")
        planos = cursor.fetchall()
        conn.close()
        return planos

    planos = carregar_planos()
    
    
    
    
    
    

    # 3) Monta feriados e horários ocupados
    feriados     = holidays.Brazil(years=agora.year)
    feriados_str = [str(d) for d in feriados]

    def horarios_ocupados():
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        ocu    = {}
        cursor.execute("SELECT data, hora FROM agendamentos_confirmados")
        for d, h in cursor.fetchall():
            ocu.setdefault(d, []).append(h)
        cursor.execute("SELECT data, hora FROM agendamentos_pendentes")
        for d, h in cursor.fetchall():
            ocu.setdefault(d, []).append(h)
        conn.close()
        return ocu

    ocupados = horarios_ocupados()

    # 4) Calcula dias bloqueados (sem agenda, fim de semana, feriados ou sem slots)
    def dias_sem_agenda(agenda, feriados, ocupados, duracao, periodos_ferias):
        bloqueados = []
        inicio     = date.today() + timedelta(days=2)
        
        # Bloquear dias de férias
        dias_ferias = set()
        for ini, fim in periodos_ferias:
            try:
                d_ini = datetime.strptime(ini, "%Y-%m-%d").date()
                d_fim = datetime.strptime(fim, "%Y-%m-%d").date()
                delta = (d_fim - d_ini).days
                for i in range(delta + 1):
                    dias_ferias.add((d_ini + timedelta(days=i)).isoformat())
            except:
                continue
        
        
        
        for i in range(60):
            dia   = inicio + timedelta(days=i)
            dstr  = dia.isoformat()
            wd    = dia.weekday()
            chave = ["segunda", "terca", "quarta", "quinta", "sexta"][wd] if wd < 5 else None

            if wd > 4 or dstr in feriados or dstr in dias_ferias or chave not in agenda:
                bloqueados.append(dstr)
            else:
                blocos = agenda[chave]
                slots  = []
                for turno in ("manha", "tarde", "noite"):
                    if blocos[turno]:
                        ini, fim = [p.strip() for p in blocos[turno].split("-")]
                        hi, mi   = map(int, ini.split(":"))
                        hf, mf   = map(int, fim.split(":"))
                        slot_dur = timedelta(minutes=duracao)
                        dt0  = datetime.combine(dia, datetime.min.time()).replace(hour=hi, minute=mi)
                        dtF  = datetime.combine(dia, datetime.min.time()).replace(hour=hf, minute=mf)
                        while dt0 + slot_dur <= dtF:
                            slots.append(dt0.strftime("%H:%M"))
                            dt0 += slot_dur
                livres = set(slots) - set(ocupados.get(dstr, []))
                if not livres:
                    bloqueados.append(dstr)

        return bloqueados

    dias_bloqueados = dias_sem_agenda(agenda, feriados_str, ocupados, duracao, periodos_ferias)
    # 5) Calcula dias disponíveis (entre 48h e 20d, sem os bloqueados)
    inicio_data = date.today() + timedelta(days=2)
    fim_data    = daqui_20d.date()
    total_dias  = (fim_data - inicio_data).days
    dias_disponiveis = [
        (inicio_data + timedelta(days=i)).isoformat()
        for i in range(total_dias + 1)
        if (inicio_data + timedelta(days=i)).isoformat() not in dias_bloqueados
    ]

    # Contexto padrão para o template
    context = {
        "data_minima": data_minima,
        "data_maxima": data_maxima,
        "agenda_json": json.dumps(agenda),
        "feriados_json": json.dumps(feriados_str),
        "horarios_ocupados_json": json.dumps(ocupados),
        "dias_bloqueados_json": json.dumps(dias_bloqueados),
        "dias_disponiveis": dias_disponiveis,
        "duracao": duracao,
        "planos": planos 
    }

    # 6) Se for POST, faz validações e grava
    if request.method == "POST":
        nome           = request.form.get("nome")
        cpf            = request.form.get("cpf")
        tel            = request.form.get("telefone")
        data_escolhida = request.form.get("data")
        hora_escolhida = request.form.get("hora")
        plano_id = request.form.get("plano_id")
        tipo_atendimento = request.form.get("tipo_atendimento")

        # 6a) Campos obrigatórios
        if not all([nome, cpf, tel, data_escolhida, hora_escolhida]):
            return render_template("agendamento.html",
                erro="Preencha todos os campos.", **context)
            
            
        escolha_dt = datetime.strptime(data_escolhida, "%Y-%m-%d")
        if escolha_dt < daqui_48h:
            return render_template("agendamento.html",
                erro="❌ A data escolhida está a menos de 48 horas. Entre em contato pelo WhatsApp para verificar disponibilidade.", **context)
                    
        if escolha_dt.date() > daqui_20d.date():
            return render_template("agendamento.html",
            erro="❌ A data escolhida está além do limite de 20 dias. Entre em contato pelo WhatsApp para ajuda.", **context)    
        if data_escolhida not in dias_disponiveis:
            return render_template("agendamento.html",
                erro="❌ A data selecionada está indisponível por motivo de agenda, feriado ou férias. Entre em contato via WhatsApp.", **context)
        
        if not hora_escolhida:
            return render_template("agendamento.html",
                erro="❌ Nenhum horário foi selecionado para essa data. Contate-nos por WhatsApp para verificar alternativas.", **context)
            

        # 6b) Verifica antecedência de 48h
        escolha_dt = datetime.strptime(data_escolhida, "%Y-%m-%d")
        if escolha_dt < daqui_48h:
            return render_template("agendamento.html",
                erro="Agendamento deve ser feito com pelo menos 48 horas de antecedência.", **context)

        # 6c) Verifica limite de 20 dias
        if escolha_dt.date() > daqui_20d.date():
            return render_template("agendamento.html",
                erro="Só é permitido agendar com até 20 dias de antecedência.", **context)

        # 6d) Verifica duplicidade e insere no banco
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM agendamentos_pendentes WHERE data=? AND hora=?",
            (data_escolhida, hora_escolhida)
        )
        if cursor.fetchone():
            conn.close()
            return render_template("agendamento.html",
                erro="Horário já reservado.", **context)

        cursor.execute("SELECT nome FROM planos_nutricionais WHERE id=?", (plano_id,))
        plano_result = cursor.fetchone()
        plano_nome = plano_result[0] if plano_result else "Plano não encontrado"

        cursor.execute(
            "INSERT INTO agendamentos_pendentes (nome, cpf, telefone, data, hora, plano_nome, tipo_atendimento) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nome, cpf, tel, data_escolhida, hora_escolhida, plano_nome, tipo_atendimento)
        )
        conn.commit()
        conn.close()
        return render_template("agendamento_enviado.html", **context)

    # 7) Se não for POST, cai aqui e renderiza a tela de agendamento
    return render_template("agendamento.html", erro="Preencha todos os campos.", **context)

        
    

@app.route("/recusar_agendamento", methods=["POST"])
@login_requerido
def recusar_agendamento():
    id_ = request.form.get("id")
    if id_:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agendamentos_pendentes WHERE id=?", (id_,))
        conn.commit()
        conn.close()
    return redirect(url_for("nutricao_painel"))





@app.route("/excluir_confirmado", methods=["POST"])
@login_requerido
def excluir_confirmado():
    id_ = request.form.get("id")
    if id_:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agendamentos_confirmados WHERE id=?", (id_,))
        conn.commit()
        conn.close()
    return redirect(url_for("nutricao_painel"))




@app.route("/salvar_paciente_confirmado", methods=["POST"])
def salvar_paciente_confirmado():
    nome = request.form.get("nome")
    cpf = request.form.get("cpf")
    telefone = request.form.get("telefone")
    data = request.form.get("data")
    hora = request.form.get("hora")
    plano = request.form.get("plano")
    tipo = request.form.get("tipo")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO agendamentos_confirmados (nome, cpf, telefone, data, hora, plano_nome, tipo_atendimento)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, cpf, telefone, data, hora, plano, tipo))
    conn.commit()
    conn.close()

    return redirect(url_for("nutricao_painel"))




























































@app.route("/adicionar_plano", methods=["POST"])
def adicionar_plano():
    nome = request.form.get("nome_plano")
    descricao = request.form.get("descricao_plano")
    valor = request.form.get("valor_plano")

    if nome and descricao and valor:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO planos_nutricionais (nome, descricao, valor) VALUES (?, ?, ?)", (nome, descricao, valor))
        conn.commit()
        conn.close()
    return redirect(url_for("agenda_nutri"))



@app.route("/excluir_plano", methods=["POST"])
def excluir_plano():
    id_ = request.form.get("id")
    if id_:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM planos_nutricionais WHERE id=?", (id_,))
        conn.commit()
        conn.close()
    return redirect(url_for("agenda_nutri"))













# Carregar os planos cadastrados
def carregar_planos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, descricao, valor FROM planos_nutricionais")
    planos = cursor.fetchall()
    conn.close()
    return planos

planos = carregar_planos()












@app.route("/salvar_ferias", methods=["POST"])
def salvar_ferias():
    data_inicio = request.form.get("ferias_inicio")
    data_fim = request.form.get("ferias_fim")

    if data_inicio and data_fim:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ferias_nutricionista (data_inicio, data_fim) VALUES (?, ?)", (data_inicio, data_fim))
        conn.commit()
        conn.close()

    return redirect(url_for("agenda_nutri"))


@app.route("/excluir_ferias", methods=["POST"])
def excluir_ferias():
    id_ = request.form.get("id")
    if id_:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ferias_nutricionista WHERE id=?", (id_,))
        conn.commit()
        conn.close()
    return redirect(url_for("agenda_nutri"))






















if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
