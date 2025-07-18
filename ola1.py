from flask import Flask, render_template, request, redirect, url_for, session

from functools import wraps

import os
import sqlite3
import json
import holidays
from datetime import datetime, timedelta, date
from datetime import datetime as dt
import re
from datetime import timedelta

#PARA APGAR AO FINAL 
app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_segura'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# força recarregamento de templates e desativa cache de estáticos em dev
app.config['TEMPLATES_AUTO_RELOAD']     = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, must-revalidate, max-age=0'
    response.headers['Pragma']        = 'no-cache'
    response.headers['Expires']       = '0'
    return response



#APAGAR 





BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH_NUTRI = os.path.join(BASE_DIR, "agenda_nutri.db")
DB_PATH_PSICO = os.path.join(BASE_DIR, "agenda_psico.db")
 
 
 
 
 
 
 
 
 
 

app.secret_key = 'uma_chave_secreta_segura'  # Troque por uma string segura
# Configurações
USUARIO = "alroka"
SENHA = "@A201810"
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




def criar_bancos():
    
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



        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acessos_pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT,
                gerado_por TEXT
            )
        """)


        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                cargo TEXT NOT NULL CHECK(cargo IN ('Nutricionista', 'Psicóloga'))
            )
        """)


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                atendimento_online BOOLEAN DEFAULT 0,
                atendimento_presencial BOOLEAN DEFAULT 0
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM config_atendimentos")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO config_atendimentos (atendimento_online, atendimento_presencial) VALUES (0, 0)")

        conn.commit()
        
        
        
        
        
    # ---- Psicóloga banco----
    with sqlite3.connect(DB_PATH_PSICO) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agenda_psicologa (
                id INTEGER PRIMARY KEY,
                dia TEXT, manha TEXT, tarde TEXT, noite TEXT,
                excluir_feriados BOOLEAN, excluir_sabado BOOLEAN,
                excluir_domingo BOOLEAN, duracao_consulta INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planos_psicologicos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                descricao TEXT,
                valor REAL NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ferias_psicologa (
                id INTEGER PRIMARY KEY,
                data_inicio TEXT,
                data_fim TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agendamentos_pendentes (
                id INTEGER PRIMARY KEY,
                nome TEXT, cpf TEXT, telefone TEXT,
                data TEXT, hora TEXT,
                plano_nome TEXT, tipo_atendimento TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agendamentos_confirmados (
                id INTEGER PRIMARY KEY,
                nome TEXT, cpf TEXT, telefone TEXT,
                data TEXT, hora TEXT,
                plano_nome TEXT, tipo_atendimento TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acessos_pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT,
                gerado_por TEXT
            )
        """)
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes_sessao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT    NOT NULL,
                telefone TEXT NOT NULL,
                dia_semana TEXT NOT NULL,
                horario TEXT   NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS galeria_fotos (
                slot     INTEGER PRIMARY KEY,  -- valores de 1 a 4
                filename TEXT    NOT NULL     -- ex: 'padrao2.png'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                atendimento_online BOOLEAN DEFAULT 0,
                atendimento_presencial BOOLEAN DEFAULT 0
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM config_atendimentos")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO config_atendimentos (atendimento_online, atendimento_presencial) VALUES (0, 0)")
                
                
        
        
        conn.commit()

            
        
DB_PATH       = os.path.join(BASE_DIR, "agenda_nutri.db")
DB_PATH_PSICO = os.path.join(BASE_DIR, "agenda_psico.db")
 
        
        
        
        
        
        
        
        
        
        
        
        
       















@app.route("/psicologia_painel", methods=["GET", "POST"])
@login_requerido
def psicologia_painel():
    conn = sqlite3.connect(DB_PATH_PSICO)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM agendamentos_pendentes "
        "WHERE datetime(data || ' ' || hora) < datetime('now', '-1 day')"
    )
    conn.commit()

    pendentes = cursor.execute(
        "SELECT * FROM agendamentos_pendentes ORDER BY data, hora"
    ).fetchall()
    confirmados = cursor.execute(
        "SELECT * FROM agendamentos_confirmados ORDER BY data, hora"
    ).fetchall()

    if request.method == "POST":
        chave = request.form.get("chave", "").strip()
        if chave:
            cursor.execute(
                "INSERT INTO acessos_pacientes (chave, gerado_por) VALUES (?, 'Psicóloga')",
                (chave,)
            )
            conn.commit()
        # Só redireciona aqui, sem fechar a conexão
        return redirect(url_for("psicologia_painel"))

    acessos = cursor.execute("""
        SELECT * FROM acessos_pacientes
         WHERE gerado_por = 'Psicóloga'
         ORDER BY id DESC
    """).fetchall()

    pacientes_sessao = cursor.execute("""
        SELECT * FROM pacientes_sessao
         ORDER BY dia_semana, horario
    """).fetchall()

    conn.close()

    return render_template(
        "psicologia.html",
        pendentes=pendentes,
        confirmados=confirmados,
        acessos=acessos,
        pacientes_sessao=pacientes_sessao
    )

    







@app.route("/excluir_chave_psico", methods=["POST"])
@login_requerido
def excluir_chave_psico():
    id_ = request.form.get("id")
    if id_:
        conn   = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM acessos_pacientes WHERE id = ?", (int(id_),))
        conn.commit()
        conn.close()
    return redirect(url_for("psicologia_painel"))





criar_bancos()
atualizar_banco_agendamentos()





# Rotas
@app.route("/", methods=["GET", "POST"])
def login():
    # → 1) SEMPRE carregue a galeria
    conn   = sqlite3.connect(DB_PATH_PSICO)
    cursor = conn.cursor()
    cursor.execute("SELECT slot, filename FROM galeria_fotos")
    rows = cursor.fetchall()
    conn.close()
    # monta dicionário {'1':'padrao1.jpg', …}
    galeria = { str(slot): filename for slot, filename in rows }
  
    
    
    
    if request.method == "POST":
        if request.form.get("usuario") == USUARIO and request.form.get("senha") == SENHA:
            session.permanent = True
            session['logado'] = True
            return redirect(url_for("bemvindo"))
       
    
        return render_template("login.html",
                                erro="Usuário ou senha incorretos.",
                                galeria=galeria)
    return render_template("login.html", galeria=galeria)




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))





@app.route("/bemvindo")
@login_requerido
def bemvindo():
    return render_template('bemvindo.html')
    
    
    





@app.route("/agenda")
@login_requerido
def agenda_nutri():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Seleciona todas as colunas relevantes para montar a agenda
    cursor.execute("""
        SELECT id, dia, manha, tarde, noite,
               excluir_feriados, excluir_sabado, excluir_domingo,
               duracao_consulta, atendimento_online, atendimento_presencial
        FROM agenda_nutricionista
    """)
    registros = cursor.fetchall()
    conn.close()

    excluir_feriados = False
    excluir_sabado = False
    excluir_domingo = False
    duracao = 30
    atendimento_online = False
    atendimento_presencial = False
    dados = {}

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
        atendimento_online = bool(linha[9])
        atendimento_presencial = bool(linha[10])

    # Carrega planos e ferias normalmente (se houver)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM planos_nutricionais ORDER BY id DESC")
    planos = cursor.fetchall()
    cursor.execute("SELECT * FROM ferias_nutricionista ORDER BY data_inicio")
    ferias = cursor.fetchall()
    conn.close()

    return render_template(
        "agenda.html",
        dados=dados,
        excluir_feriados=excluir_feriados,
        excluir_sabado=excluir_sabado,
        excluir_domingo=excluir_domingo,
        duracao=duracao,
        atendimento_online=atendimento_online,
        atendimento_presencial=atendimento_presencial,
        planos=planos,
        ferias=ferias
    )





     
     
     
                           
@app.route("/salvar_agenda", methods=["POST"])
@login_requerido
def salvar_agenda():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    dias = request.form.getlist("dias")
    print("Dias marcados:", dias)

    # Captura flags dos checkboxes
    online     = 'atendimento_online'     in request.form
    presencial = 'atendimento_presencial' in request.form
    excluir_feriados = 'excluir_feriados' in request.form
    excluir_sabado   = False
    excluir_domingo  = False
    duracao = int(request.form.get("duracao"))

    # Limpa registros anteriores
    cursor.execute("DELETE FROM agenda_nutricionista")

    prefixos = {
        "segunda": "seg",
        "terca":   "ter",
        "quarta":  "qua",
        "quinta":  "qui",
        "sexta":   "sex"
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
                dia,
                manha,
                tarde,
                noite,
                excluir_feriados,
                excluir_sabado,
                excluir_domingo,
                duracao_consulta,
                atendimento_online,
                atendimento_presencial
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dia,
            manha,
            tarde,
            noite,
            int(excluir_feriados),
            int(excluir_sabado),
            int(excluir_domingo),
            duracao,
            int(online),
            int(presencial)
        ))

    conn.commit()
    conn.close()

    return redirect(url_for("nutricao_painel"))


















@app.route("/salvar_atendimentos", methods=["POST"])
@login_requerido
def salvar_atendimentos():
    atendimento_online = 'atendimento_online' in request.form
    atendimento_presencial = 'atendimento_presencial' in request.form

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verifica se já existe um registro
    cursor.execute("SELECT id FROM config_atendimentos LIMIT 1")
    row = cursor.fetchone()

    if not row:
        # Insere um registro padrão se não existir
        cursor.execute(
            "INSERT INTO config_atendimentos (atendimento_online, atendimento_presencial) VALUES (?, ?)",
            (atendimento_online, atendimento_presencial)
        )
        conn.commit()
        cursor.execute("SELECT id FROM config_atendimentos LIMIT 1")
        row = cursor.fetchone()

    id_config = row[0]

    # Atualiza os valores
    cursor.execute("""
        UPDATE config_atendimentos SET
            atendimento_online = ?,
            atendimento_presencial = ?
        WHERE id = ?
    """, (atendimento_online, atendimento_presencial, id_config))

    conn.commit()
    conn.close()

    return redirect(url_for("agenda_nutri"))






@app.route("/nutricao_painel", methods=["GET", "POST"])
@login_requerido
def nutricao_painel():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Limpa pendentes muito antigos
    cursor.execute(
        "DELETE FROM agendamentos_pendentes "
        "WHERE datetime(data || ' ' || hora) < datetime('now', '-1 day')"
    )

    # Busca pendentes e confirmados
    cursor.execute("SELECT * FROM agendamentos_pendentes ORDER BY data, hora")
    pendentes = cursor.fetchall()
    cursor.execute("SELECT * FROM agendamentos_confirmados ORDER BY data, hora")
    confirmados = cursor.fetchall()

    if request.method == "POST":
        chave = request.form.get("chave", "").strip()
        gerado_por = "Nutricionista"
        if chave:
            cursor.execute(
                "INSERT INTO acessos_pacientes (chave, gerado_por) VALUES (?, ?)",
                (chave, gerado_por)
            )
            conn.commit()
        # Não fechar conexão aqui, apenas redirecionar
        return redirect(url_for("nutricao_painel"))

    # GET: carrega só as chaves do Nutricionista
    cursor.execute("""
        SELECT * FROM acessos_pacientes
        WHERE gerado_por = 'Nutricionista'
        ORDER BY id DESC
    """)
    acessos = cursor.fetchall()
    conn.close()

    return render_template(
        "nutricao.html",
        pendentes=pendentes,
        confirmados=confirmados,
        acessos=acessos
    )
















from flask import Flask, render_template, request, redirect, url_for
import sqlite3, json, holidays
from datetime import datetime, timedelta, date
# Rota de agendamento da NUTRICIONISTA
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
        if not re.fullmatch(r"55\d{10,11}", tel):
            return render_template("agendamento.html",
                erro="❌ Telefone inválido. Use o formato 55DDXXXXXXXXX (ex: 5531999998888).", **context)
                
        
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





@app.route("/chaves_acesso", methods=["GET", "POST"])
@login_requerido
def chaves_acesso():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Criar a tabela, se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acessos_pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT,
            gerado_por TEXT
        )
    """)

    # Inserir nova chave (se POST)
    if request.method == "POST":
        chave = request.form.get("chave")
        gerado_por = request.form.get("gerado_por")
        if chave and gerado_por:
            cursor.execute("INSERT INTO acessos_pacientes (chave, gerado_por) VALUES (?, ?)", (chave, gerado_por))
            conn.commit()

    # Buscar todos os acessos para exibir
    cursor.execute("SELECT * FROM acessos_pacientes ORDER BY id DESC")
    acessos = cursor.fetchall()
    conn.close()
    return render_template("chaves_acesso.html", acessos=acessos)


@app.route("/excluir_chave", methods=["POST"])
@login_requerido
def excluir_chave():
    try:
        id_ = request.form.get("id")
        print("ID recebido para exclusão:", id_)
        if id_:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM acessos_pacientes WHERE id=?", (int(id_),))
            conn.commit()
            conn.close()
        else:
            print("⚠️ Nenhum ID recebido.")
    except Exception as e:
        print("❌ Erro ao excluir chave:", e)
    return redirect(url_for("nutricao_painel"))




@app.route("/acesso_paciente")
def acesso_paciente():
    return render_template("acesso_paciente.html")







@app.route("/verificar_chave", methods=["POST"])
def verificar_chave():
    chave = request.form.get("chave", "").strip()
    if not chave:
        return "Chave não fornecida", 400

    # 1) procura no banco da Nutri
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT gerado_por FROM acessos_pacientes WHERE chave = ?", (chave,))
    resultados = cursor.fetchall()
    conn.close()

    # 2) se não achou nada, procura no banco da Psico
    if not resultados:
        conn = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        cursor.execute("SELECT gerado_por FROM acessos_pacientes WHERE chave = ?", (chave,))
        resultados = cursor.fetchall()
        conn.close()

    # 3) se ainda não achou, dá erro
    if not resultados:
        return "❌ Chave inválida ou não encontrada.", 404

    # 4) decide para onde redirecionar
    tipos = {r[0] for r in resultados}
    if tipos == {"Nutricionista"}:
        return redirect(url_for("pacientenutricionista"))
    elif tipos == {"Psicóloga"}:
        return redirect(url_for("pacientepsicologia"))
    else:
        # se, por acaso, a mesma chave foi gerada em ambos os bancos
        return render_template("abrir_duas_abas.html")









@app.route("/pacientenutricionista")
def pacientenutricionista():
    return render_template("pacientenutricionista.html")

@app.route("/pacientepsicologia")
def pacientepsicologia():
    return render_template("pacientepsicologia.html")





from flask import render_template_string, request, redirect, url_for
import sqlite3
import urllib.parse

@app.route("/confirmar_agendamento", methods=["POST"])
@login_requerido
def confirmar_agendamento():
    id_ = request.form.get("id")
    if not id_:
        return redirect(url_for("nutricao_painel"))

    # Banco
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agendamentos_pendentes WHERE id=?", (id_,))
    agendamento = cursor.fetchone()

    if agendamento:
        cursor.execute("""
            INSERT INTO agendamentos_confirmados (nome, cpf, telefone, data, hora, plano_nome, tipo_atendimento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, agendamento[1:])
        cursor.execute("DELETE FROM agendamentos_pendentes WHERE id=?", (id_,))
        conn.commit()
    conn.close()

    # Dados do paciente
    nome = agendamento[1]
    telefone = agendamento[3].replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    telefone_formatado = f"55{telefone}" if not telefone.startswith("55") else telefone
    data = agendamento[4]
    hora = agendamento[5]
    mensagem = f"Olá {nome}, seu agendamento foi confirmado para o dia {data} às {hora}. Atenciosamente, PsiconutriSaúde. Até breve!"
    mensagem_encoded = urllib.parse.quote(mensagem)

    # URL que funciona para celular e PC
    whatsapp_url = f"https://wa.me/{telefone_formatado}?text={mensagem_encoded}"

    # Retorna HTML com JavaScript que abre em nova aba
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
      <meta charset="UTF-8">
      <title>WhatsApp</title>
      <script>
        window.onload = function() {{
          window.open("{whatsapp_url}", "_blank");
          setTimeout(function() {{
            window.location.href = "{url_for('nutricao_painel')}";
          }}, 2000);
        }};
      </script>
    </head>
    <body>
      <p>Agendamento confirmado! Abrindo WhatsApp em nova aba...</p>
    </body>
    </html>
    """)







#Início psicologia 



@app.route("/salvar_agenda_psicologia", methods=["POST"])
@login_requerido
def salvar_agenda_psicologia():
    conn = sqlite3.connect(DB_PATH_PSICO)
    cursor = conn.cursor()
    online     = 'atendimento_online' in request.form
    presencial = 'atendimento_presencial' in request.form

    dias = request.form.getlist("dias")
    duracao = int(request.form.get("duracao"))
    excluir_feriados = bool(request.form.get("excluir_feriados"))

    cursor.execute("DELETE FROM agenda_psicologa")

    prefixos = {
        "segunda": "seg",
        "terca": "ter",
        "quarta": "qua",
        "quinta": "qui",
        "sexta": "sex"
    }

    for dia in dias:
        prefixo = prefixos.get(dia)
        manha = request.form.get(f"manha_{prefixo}", "")
        tarde = request.form.get(f"tarde_{prefixo}", "")
        noite = request.form.get(f"noite_{prefixo}", "")

        cursor.execute("""
            INSERT INTO agenda_psicologa (dia, manha, tarde, noite, excluir_feriados, excluir_sabado, excluir_domingo, duracao_consulta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (dia, manha, tarde, noite, excluir_feriados, False, False, duracao))

    conn.commit()
    conn.close()
    return redirect(url_for("psicologia_painel"))





@app.route("/agenda_psicologia")
@login_requerido
def agenda_psicologia():
    print("Rota /agenda_psicologia acessada corretamente!")
    conn = sqlite3.connect(DB_PATH_PSICO)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agenda_psicologa")
    registros = cursor.fetchall()

    cursor.execute("SELECT * FROM planos_psicologicos ORDER BY id DESC")
    planos = cursor.fetchall()

    cursor.execute("SELECT * FROM ferias_psicologa ORDER BY data_inicio")
    ferias = cursor.fetchall()

    conn.close()

    dados = {}
    excluir_feriados = False
    duracao = 50  # duração padrão

    for linha in registros:
        dia = linha[1]
        dados[dia] = {
            "manha": linha[2],
            "tarde": linha[3],
            "noite": linha[4]
        }
        excluir_feriados = linha[5]
        duracao = linha[8]

    return render_template("psicologia_agenda.html", dados=dados,
                           excluir_feriados=excluir_feriados,
                           duracao=duracao,
                           planos=planos,
                           ferias=ferias)







@app.route("/adicionar_plano_psicologa", methods=["POST"])
def adicionar_plano_psicologa():
    nome = request.form.get("nome_plano")
    descricao = request.form.get("descricao_plano")
    valor = request.form.get("valor_plano")

    if not nome or not valor:
        return "Nome e valor são obrigatórios!", 400

    try:
        valor_float = float(str(valor).replace(",", "."))
    except ValueError:
        return "Valor inválido!", 400

    with sqlite3.connect(DB_PATH_PSICO) as conn:  # <-- Corrigido aqui
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO planos_psicologicos (nome, descricao, valor)
            VALUES (?, ?, ?)
        """, (nome, descricao, valor_float))
        conn.commit()

    return redirect("/agenda_psicologia")


@app.route("/excluir_plano_psicologico", methods=["POST"])
@login_requerido
def excluir_plano_psicologico():
    id_ = request.form.get("id")
    if id_:
        conn = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM planos_psicologicos WHERE id=?", (id_,))
        conn.commit()
        conn.close()
    return redirect(url_for("agenda_psicologia"))





# Rota de agendamento da PSICÓLOGA
@app.route("/agendar_psicologia", methods=["GET", "POST"])
def agendar_psicologia():
    # 1) Define limites para agendamento (mínimo 48h, máximo 20 dias à frente)
    agora     = datetime.now()
    daqui_48h = agora + timedelta(hours=48)
    daqui_20d = agora + timedelta(days=20)
    data_minima = daqui_48h.date().isoformat()
    data_maxima = daqui_20d.date().isoformat()

    # 2) Carrega períodos de férias da psicóloga
    conn = sqlite3.connect(DB_PATH_PSICO)
    cursor = conn.cursor()
    cursor.execute("SELECT data_inicio, data_fim FROM ferias_psicologa")
    periodos_ferias = cursor.fetchall()
    conn.close()

    # 3) Carrega agenda semanal e duração das consultas
    def carregar_agenda():
        conn = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agenda_psicologa")
        linhas = cursor.fetchall()
        conn.close()
        agenda = {}
        duracao = 50
        for linha in linhas:
            dia = linha[1]
            agenda[dia] = {
                "manha": linha[2],
                "tarde": linha[3],
                "noite": linha[4]
            }
            duracao = linha[8]
        return agenda, duracao

    agenda, duracao = carregar_agenda()

    # 4) Carrega lista de planos psicológicos
    def carregar_planos():
        conn = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao, valor FROM planos_psicologicos")
        planos = cursor.fetchall()
        conn.close()
        return planos

    planos = carregar_planos()

    # 5) Lista de feriados nacionais
    feriados = holidays.Brazil(years=agora.year)
    feriados_str = [str(d) for d in feriados]

    # 6) Coleta horários já ocupados nos agendamentos pendentes e confirmados
    def horarios_ocupados():
        conn = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        ocu = {}

        # 1) Carrega agendamentos confirmados e pendentes
        cursor.execute("SELECT data, hora FROM agendamentos_confirmados WHERE tipo_atendimento='Psicóloga'")
        for d, h in cursor.fetchall():
            ocu.setdefault(d, []).append(h)
        cursor.execute("SELECT data, hora FROM agendamentos_pendentes WHERE tipo_atendimento='Psicóloga'")
        for d, h in cursor.fetchall():
            ocu.setdefault(d, []).append(h)

        # 2) Carrega sessões fixas (pacientes_sessao)
        cursor.execute("SELECT dia_semana, horario FROM pacientes_sessao")
        sessoes = cursor.fetchall()
        conn.close()

        # Mapeia nome do dia para weekday
        dia_map = {
            "Segunda": 0, "Terça": 1, "Quarta": 2,
            "Quinta": 3,  "Sexta": 4
        }

        # Para os próximos 60 dias, bloqueia o horário fixo em cada data correspondente
        hoje_mais_2 = date.today() + timedelta(days=2)
        for dia_semana, horario in sessoes:
            wd = dia_map.get(dia_semana)
            if wd is None:
                continue
            for i in range(60):
                d = hoje_mais_2 + timedelta(days=i)
                if d.weekday() == wd:
                    ocu.setdefault(d.isoformat(), []).append(horario)

        return ocu

    ocupados = horarios_ocupados()








    # 7) Calcula dias bloqueados (fim de semana, feriados, férias ou sem horários livres)
    def dias_sem_agenda(agenda, feriados, ocupados, duracao, periodos_ferias):
        bloqueados = []
        hoje_mais_2 = date.today() + timedelta(days=2)

        # marca todos os dias de férias
        dias_ferias = set()
        for inicio, fim in periodos_ferias:
            try:
                d0 = datetime.strptime(inicio, "%Y-%m-%d").date()
                d1 = datetime.strptime(fim, "%Y-%m-%d").date()
                for i in range((d1 - d0).days + 1):
                    dias_ferias.add((d0 + timedelta(days=i)).isoformat())
            except:
                pass

        # checa 60 dias para montar bloqueios
        for i in range(60):
            dia = hoje_mais_2 + timedelta(days=i)
            dstr = dia.isoformat()
            wd = dia.weekday()
            chave = ["segunda","terca","quarta","quinta","sexta"][wd] if wd < 5 else None

            if wd > 4 or dstr in feriados or dstr in dias_ferias or chave not in agenda:
                bloqueados.append(dstr)
                continue

            # gera slots a cada 'duracao' minutos
            slots = []
            blocos = agenda[chave]
            for turno in ("manha","tarde","noite"):
                if blocos[turno]:
                    try:
                        ini_h, fim_h = blocos[turno].split("-")
                        hi, mi = map(int, ini_h.strip().split(":"))
                        hf, mf = map(int, fim_h.strip().split(":"))
                        t0 = datetime.combine(dia, datetime.min.time()).replace(hour=hi, minute=mi)
                        tF = datetime.combine(dia, datetime.min.time()).replace(hour=hf, minute=mf)
                        while t0 + timedelta(minutes=duracao) <= tF:
                            slots.append(t0.strftime("%H:%M"))
                            t0 += timedelta(minutes=duracao)
                    except:
                        pass

            livres = set(slots) - set(ocupados.get(dstr, []))
            if not livres:
                bloqueados.append(dstr)

        return bloqueados

    dias_bloqueados = dias_sem_agenda(agenda, feriados_str, ocupados, duracao, periodos_ferias)

    # 8) Calcula datas disponíveis entre 48h e 20 dias à frente
    inicio_data = date.today() + timedelta(days=2)
    fim_data    = daqui_20d.date()
    total_dias  = (fim_data - inicio_data).days
    dias_disponiveis = [
        (inicio_data + timedelta(days=i)).isoformat()
        for i in range(total_dias + 1)
        if (inicio_data + timedelta(days=i)).isoformat() not in dias_bloqueados
    ]

    # Contexto para o template
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

    # 9) Se for POST, processa o envio de formulário
    if request.method == "POST":
        nome             = request.form.get("nome")
        cpf              = request.form.get("cpf")
        tel              = request.form.get("telefone")
        data_escolhida   = request.form.get("data")
        hora_escolhida   = request.form.get("hora")
        plano_id         = request.form.get("plano_id")
        tipo_atendimento = request.form.get("tipo_atendimento")

        # validações básicas
        if not re.fullmatch(r"55\d{10,11}", tel):
            return render_template("psicologia_agendamento.html", erro="❌ Telefone inválido.", **context)
        if not all([nome, cpf, tel, data_escolhida, hora_escolhida]):
            return render_template("psicologia_agendamento.html", erro="Preencha todos os campos.", **context)
        escolha_dt = datetime.strptime(data_escolhida, "%Y-%m-%d")
        if escolha_dt < daqui_48h:
            return render_template("psicologia_agendamento.html", erro="❌ Menos de 48h de antecedência.", **context)
        if escolha_dt.date() > daqui_20d.date():
            return render_template("psicologia_agendamento.html", erro="❌ Além de 20 dias.", **context)
        if data_escolhida not in dias_disponiveis:
            return render_template("psicologia_agendamento.html", erro="❌ Data indisponível.", **context)

        conn = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()

        # verifica duplicidade
        cursor.execute(
            "SELECT 1 FROM agendamentos_pendentes WHERE data=? AND hora=? AND tipo_atendimento='Psicóloga'",
            (data_escolhida, hora_escolhida)
        )
        if cursor.fetchone():
            conn.close()
            return render_template("psicologia_agendamento.html", erro="❌ Horário reservado.", **context)

        # busca o nome do plano apenas uma vez
        cursor.execute("SELECT nome FROM planos_psicologicos WHERE id = ?", (plano_id,))
        row = cursor.fetchone()
        plano_nome = row[0] if row else "Plano não encontrado"

        # insere no banco com o tipo escolhido
        cursor.execute("""
            INSERT INTO agendamentos_pendentes
              (nome, cpf, telefone, data, hora, plano_nome, tipo_atendimento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, cpf, tel, data_escolhida, hora_escolhida, plano_nome, tipo_atendimento))
        conn.commit()
        conn.close()

        return render_template("agendamento_enviado.html", **context)

    # 10) Se GET, apenas renderiza o formulário
    return render_template("psicologia_agendamento.html", **context)












@app.route("/confirmar_agendamento_psico", methods=["POST"])
@login_requerido
def confirmar_agendamento_psico():
    id_ = request.form.get("id")
    if not id_:
        return redirect(url_for("psicologia_painel"))

    conn = sqlite3.connect(DB_PATH_PSICO)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agendamentos_pendentes WHERE id=?", (id_,))
    agendamento = cursor.fetchone()

    if agendamento:
        cursor.execute("""
            INSERT INTO agendamentos_confirmados (nome, cpf, telefone, data, hora, plano_nome, tipo_atendimento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, agendamento[1:])
        cursor.execute("DELETE FROM agendamentos_pendentes WHERE id=?", (id_,))
        conn.commit()

    conn.close()
    return redirect(url_for("psicologia_painel"))


@app.route("/recusar_agendamento_psico", methods=["POST"])
@login_requerido
def recusar_agendamento_psico():
    id_ = request.form.get("id")
    if id_:
        conn = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agendamentos_pendentes WHERE id=?", (id_,))
        conn.commit()
        conn.close()
    return redirect(url_for("psicologia_painel"))



@app.route("/excluir_confirmado_psico", methods=["POST"])
@login_requerido
def excluir_confirmado_psico():
    id_ = request.form["id"]
    conn = sqlite3.connect(DB_PATH_PSICO)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos_confirmados WHERE id = ?", (id_,))
    conn.commit()
    conn.close()
    return redirect(url_for("psicologia_painel"))




@app.route("/salvar_paciente_confirmado_psico", methods=["POST"])
@login_requerido
def salvar_paciente_confirmado_psico():
    nome      = request.form["nome"]
    cpf       = request.form["cpf"]
    telefone  = request.form["telefone"]
    data      = request.form["data"]
    hora      = request.form["hora"]
    plano     = request.form["plano"]
    tipo      = request.form["tipo"]

    conn = sqlite3.connect(DB_PATH_PSICO)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO agendamentos_confirmados
          (nome, cpf, telefone, data, hora, plano_nome, tipo_atendimento)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, cpf, telefone, data, hora, plano, tipo))
    conn.commit()
    conn.close()

    return redirect(url_for("psicologia_painel"))








@app.route("/salvar_ferias_psicologa", methods=["POST"])
@login_requerido
def salvar_ferias_psicologa():
    data_inicio = request.form.get("ferias_inicio")
    data_fim    = request.form.get("ferias_fim")

    if data_inicio and data_fim:
        conn   = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ferias_psicologa (data_inicio, data_fim) VALUES (?, ?)",
            (data_inicio, data_fim)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("agenda_psicologia"))


@app.route("/excluir_ferias_psicologa", methods=["POST"])
@login_requerido
def excluir_ferias_psicologa():
    id_ = request.form.get("id")
    if id_:
        conn   = sqlite3.connect(DB_PATH_PSICO)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM ferias_psicologa WHERE id = ?",
            (id_,)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("agenda_psicologia"))






@app.route('/salvar_paciente_sessao', methods=['POST'])
@login_requerido
def salvar_paciente_sessao():
    nome = request.form['nome']
    tel  = request.form['telefone']
    dia  = request.form['dia_semana']
    hor  = request.form['horario']
    conn = sqlite3.connect(DB_PATH_PSICO)
    c = conn.cursor()
    c.execute('''
      INSERT INTO pacientes_sessao (nome, telefone, dia_semana, horario)
      VALUES (?, ?, ?, ?)
    ''', (nome, tel, dia, hor))
    conn.commit()
    conn.close()
    return redirect(url_for('psicologia_painel'))

@app.route('/excluir_paciente_sessao', methods=['POST'])
@login_requerido
def excluir_paciente_sessao():
    id_ = request.form['id']
    conn = sqlite3.connect(DB_PATH_PSICO)
    c = conn.cursor()
    c.execute('DELETE FROM pacientes_sessao WHERE id=?', (id_,))
    conn.commit()
    conn.close()
    return redirect(url_for('psicologia_painel'))





























from werkzeug.utils import secure_filename

@app.route('/upload_foto', methods=['POST'])
@login_requerido
def upload_foto():
    slot    = request.form.get('slot')        # "1", "2", "3" ou "4"
    arquivo = request.files.get('arquivo')
    if not slot or not arquivo:
        return redirect(url_for('login'))      # ou 'bemvindo', conforme você queira

    # 1) Garante nome seguro, mantendo extensão
    original = secure_filename(arquivo.filename)
    ext      = os.path.splitext(original)[1] or '.jpg'
    nome     = f'padrao{slot}{ext}'
    destino  = os.path.join(app.static_folder, 'img', nome)
    arquivo.save(destino)

    # 2) Insere ou atualiza no banco
    conn = sqlite3.connect(DB_PATH_PSICO)
    c    = conn.cursor()
    c.execute("""
      INSERT INTO galeria_fotos (slot, filename)
      VALUES (?, ?)
      ON CONFLICT(slot) DO UPDATE SET filename=excluded.filename
    """, (int(slot), nome))
    conn.commit()
    conn.close()

    return redirect(url_for('bemvindo'))




@app.before_request
def refresh_session():
    session.modified = True



@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response



def corrigir_tabela_agenda_nutricionista():
    conn = sqlite3.connect("agenda_nutri.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(agenda_nutricionista)")
    colunas = [col[1] for col in cursor.fetchall()]

    if "atendimento_online" not in colunas:
        cursor.execute("ALTER TABLE agenda_nutricionista ADD COLUMN atendimento_online BOOLEAN DEFAULT 0")
        print("✔️ Coluna atendimento_online adicionada.")

    if "atendimento_presencial" not in colunas:
        cursor.execute("ALTER TABLE agenda_nutricionista ADD COLUMN atendimento_presencial BOOLEAN DEFAULT 0")
        print("✔️ Coluna atendimento_presencial adicionada.")

    conn.commit()
    conn.close()

corrigir_tabela_agenda_nutricionista()











if __name__ == "__main__":
    criar_bancos()
    atualizar_banco_agendamentos()  # Se quiser manter isso como suporte
    app.run(host="0.0.0.0", port=5000, debug=True)