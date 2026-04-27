from datetime import datetime, timedelta
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "plataforma-cursos-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plataforma.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Faca login para continuar."


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tipo = db.Column(db.String(20), nullable=False, default="aluno")

    cursos_criados = db.relationship("Curso", backref="instrutor", lazy=True)
    matriculas = db.relationship("Matricula", backref="usuario", lazy=True)
    progressos = db.relationship("ProgressoAula", backref="usuario", lazy=True)
    avaliacoes = db.relationship("Avaliacao", backref="usuario", lazy=True)
    certificados = db.relationship("Certificado", backref="usuario", lazy=True)
    assinaturas = db.relationship("Assinatura", backref="usuario", lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def nome(self):
        return self.nome_completo


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    cursos = db.relationship("Curso", backref="categoria_rel", lazy=True)
    trilhas = db.relationship("Trilha", backref="categoria_rel", lazy=True)


class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    instrutor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    nivel = db.Column(db.String(30), nullable=False)
    data_publicacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_aulas = db.Column(db.Integer, nullable=False, default=0)
    total_horas = db.Column(db.Float, nullable=False, default=0.0)

    modulos = db.relationship("Modulo", backref="curso", lazy=True, cascade="all, delete-orphan")
    matriculas = db.relationship("Matricula", backref="curso", lazy=True, cascade="all, delete-orphan")
    avaliacoes = db.relationship("Avaliacao", backref="curso", lazy=True, cascade="all, delete-orphan")
    certificados = db.relationship("Certificado", backref="curso", lazy=True, cascade="all, delete-orphan")
    trilhas_cursos = db.relationship("TrilhaCurso", backref="curso", lazy=True, cascade="all, delete-orphan")

    @property
    def categoria(self):
        return self.categoria_rel.nome if self.categoria_rel else ""

    @property
    def media_avaliacoes(self):
        if not self.avaliacoes:
            return None
        return round(sum(item.nota for item in self.avaliacoes) / len(self.avaliacoes), 1)

    @property
    def total_matriculas(self):
        return len(self.matriculas)


class Modulo(db.Model):
    __tablename__ = "modulos"

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    ordem = db.Column(db.Integer, nullable=False, default=1)

    aulas = db.relationship("Aula", backref="modulo", lazy=True, cascade="all, delete-orphan")


class Aula(db.Model):
    __tablename__ = "aulas"

    id = db.Column(db.Integer, primary_key=True)
    modulo_id = db.Column(db.Integer, db.ForeignKey("modulos.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    tipo_conteudo = db.Column(db.String(30), nullable=False)
    url_conteudo = db.Column(db.String(255), nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False, default=0)
    ordem = db.Column(db.Integer, nullable=False, default=1)

    progressos = db.relationship("ProgressoAula", backref="aula", lazy=True, cascade="all, delete-orphan")


class Matricula(db.Model):
    __tablename__ = "matriculas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    data_matricula = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint("usuario_id", "curso_id", name="uq_usuario_curso"),)


class ProgressoAula(db.Model):
    __tablename__ = "progresso_aulas"

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), primary_key=True)
    aula_id = db.Column(db.Integer, db.ForeignKey("aulas.id"), primary_key=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Concluido")


class Avaliacao(db.Model):
    __tablename__ = "avaliacoes"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    data_avaliacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("usuario_id", "curso_id", name="uq_avaliacao_usuario_curso"),)


class Trilha(db.Model):
    __tablename__ = "trilhas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)

    cursos = db.relationship("TrilhaCurso", backref="trilha", lazy=True, cascade="all, delete-orphan")
    certificados = db.relationship("Certificado", backref="trilha", lazy=True)


class TrilhaCurso(db.Model):
    __tablename__ = "trilhas_cursos"

    trilha_id = db.Column(db.Integer, db.ForeignKey("trilhas.id"), primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), primary_key=True)
    ordem = db.Column(db.Integer, nullable=False, default=1)


class Certificado(db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    trilha_id = db.Column(db.Integer, db.ForeignKey("trilhas.id"), nullable=True)
    codigo_verificacao = db.Column(db.String(60), unique=True, nullable=False)
    data_emissao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Plano(db.Model):
    __tablename__ = "planos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False)
    duracao_meses = db.Column(db.Integer, nullable=False)

    assinaturas = db.relationship("Assinatura", backref="plano", lazy=True)


class Assinatura(db.Model):
    __tablename__ = "assinaturas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    plano_id = db.Column(db.Integer, db.ForeignKey("planos.id"), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)

    pagamentos = db.relationship("Pagamento", backref="assinatura", lazy=True, cascade="all, delete-orphan")


class Pagamento(db.Model):
    __tablename__ = "pagamentos"

    id = db.Column(db.Integer, primary_key=True)
    assinatura_id = db.Column(db.Integer, db.ForeignKey("assinaturas.id"), nullable=False)
    valor_pago = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    metodo_pagamento = db.Column(db.String(60), nullable=False)
    id_transacao_gateway = db.Column(db.String(120), nullable=False)
    data_fim = db.Column(db.Date, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


def texto_limpo(campo):
    return request.form.get(campo, "").strip()


def usuario_ja_matriculado(usuario_id, curso_id):
    return Matricula.query.filter_by(usuario_id=usuario_id, curso_id=curso_id).first() is not None


def progresso_aula(usuario_id, aula_id):
    return ProgressoAula.query.filter_by(usuario_id=usuario_id, aula_id=aula_id).first()


def atualizar_estatisticas_curso(curso):
    aulas = Aula.query.join(Modulo).filter(Modulo.curso_id == curso.id).all()
    curso.total_aulas = len(aulas)
    curso.total_horas = round(sum(aula.duracao_minutos for aula in aulas) / 60, 1) if aulas else 0.0


def gerar_certificado(usuario_id, curso_id):
    certificado = Certificado.query.filter_by(usuario_id=usuario_id, curso_id=curso_id).first()
    if certificado:
        return certificado

    certificado = Certificado(
        usuario_id=usuario_id,
        curso_id=curso_id,
        codigo_verificacao=str(uuid4()).replace("-", "").upper(),
    )
    db.session.add(certificado)
    return certificado


def concluir_curso_se_necessario(usuario_id, curso):
    aulas = (
        Aula.query.join(Modulo)
        .filter(Modulo.curso_id == curso.id)
        .order_by(Modulo.ordem.asc(), Aula.ordem.asc())
        .all()
    )
    if not aulas:
        return

    aula_ids = {aula.id for aula in aulas}
    progressos = ProgressoAula.query.filter(
        ProgressoAula.usuario_id == usuario_id,
        ProgressoAula.aula_id.in_(aula_ids),
    ).all()
    concluidas = {item.aula_id for item in progressos if item.status == "Concluido"}

    if aula_ids.issubset(concluidas):
        matricula = Matricula.query.filter_by(usuario_id=usuario_id, curso_id=curso.id).first()
        if matricula and matricula.data_conclusao is None:
            matricula.data_conclusao = datetime.utcnow()
            gerar_certificado(usuario_id, curso.id)


@app.context_processor
def inject_helpers():
    return {
        "usuario_ja_matriculado": usuario_ja_matriculado,
        "progresso_aula": progresso_aula,
    }


@app.route("/")
def index():
    busca = request.args.get("busca", "").strip()
    categoria = request.args.get("categoria", "").strip()

    query = Curso.query.order_by(Curso.id.desc())

    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            or_(Curso.titulo.ilike(termo), Curso.descricao.ilike(termo), Curso.nivel.ilike(termo))
        )

    if categoria:
        query = query.join(Categoria).filter(func.lower(Categoria.nome) == categoria.lower())

    cursos = query.all()
    categorias = Categoria.query.order_by(Categoria.nome.asc()).all()
    trilhas = Trilha.query.order_by(Trilha.titulo.asc()).all()
    planos = Plano.query.order_by(Plano.preco.asc()).all()

    destaques = {
        "total_cursos": Curso.query.count(),
        "total_instrutores": Usuario.query.filter_by(tipo="instrutor").count(),
        "total_alunos": Usuario.query.filter_by(tipo="aluno").count(),
        "total_matriculas": Matricula.query.count(),
    }

    return render_template(
        "index.html",
        busca=busca,
        categoria_ativa=categoria,
        categorias=categorias,
        cursos=cursos,
        trilhas=trilhas,
        planos=planos,
        destaques=destaques,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        nome = texto_limpo("nome")
        email = texto_limpo("email").lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")
        tipo = texto_limpo("tipo") or "aluno"

        if not nome or not email or not senha:
            flash("Preencha todos os campos obrigatorios.")
            return render_template("register.html")

        if tipo not in {"aluno", "instrutor"}:
            flash("Tipo de usuario invalido.")
            return render_template("register.html")

        if len(senha) < 6:
            flash("A senha precisa ter pelo menos 6 caracteres.")
            return render_template("register.html")

        if senha != confirmar_senha:
            flash("As senhas nao coincidem.")
            return render_template("register.html")

        if Usuario.query.filter_by(email=email).first():
            flash("Ja existe um usuario cadastrado com esse e-mail.")
            return render_template("register.html")

        usuario = Usuario(nome_completo=nome, email=email, tipo=tipo)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()

        flash("Conta criada com sucesso. Agora faca login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = texto_limpo("email").lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario is None or not usuario.check_senha(senha):
            flash("E-mail ou senha invalidos.")
            return render_template("login.html")

        login_user(usuario)
        flash(f"Bem-vindo, {usuario.nome}.")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sessao encerrada com sucesso.")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    certificados = Certificado.query.filter_by(usuario_id=current_user.id).all()
    assinatura = (
        Assinatura.query.filter_by(usuario_id=current_user.id)
        .order_by(Assinatura.data_fim.desc())
        .first()
    )

    if current_user.tipo == "instrutor":
        meus_cursos = Curso.query.filter_by(instrutor_id=current_user.id).order_by(Curso.id.desc()).all()
        categorias = Categoria.query.order_by(Categoria.nome.asc()).all()
        return render_template(
            "dashboard.html",
            meus_cursos=meus_cursos,
            cursos_matriculados=[],
            certificados=certificados,
            assinatura=assinatura,
            categorias=categorias,
        )

    cursos_matriculados = (
        db.session.query(Curso)
        .join(Matricula, Matricula.curso_id == Curso.id)
        .filter(Matricula.usuario_id == current_user.id)
        .order_by(Curso.id.desc())
        .all()
    )
    return render_template(
        "dashboard.html",
        meus_cursos=[],
        cursos_matriculados=cursos_matriculados,
        certificados=certificados,
        assinatura=assinatura,
        categorias=[],
    )


@app.route("/categoria/nova", methods=["POST"])
@login_required
def nova_categoria():
    if current_user.tipo != "instrutor":
        flash("Apenas instrutores podem cadastrar categorias.")
        return redirect(url_for("dashboard"))

    nome = texto_limpo("nome")
    descricao = texto_limpo("descricao")

    if not nome:
        flash("Informe o nome da categoria.")
        return redirect(url_for("dashboard"))

    existente = Categoria.query.filter(func.lower(Categoria.nome) == nome.lower()).first()
    if existente:
        flash("Essa categoria ja existe.")
        return redirect(url_for("dashboard"))

    categoria = Categoria(nome=nome, descricao=descricao or None)
    db.session.add(categoria)
    db.session.commit()
    flash("Categoria criada com sucesso.")
    return redirect(url_for("novo_curso"))


@app.route("/curso/novo", methods=["GET", "POST"])
@login_required
def novo_curso():
    if current_user.tipo != "instrutor":
        flash("Apenas instrutores podem criar cursos.")
        return redirect(url_for("dashboard"))

    categorias = Categoria.query.order_by(Categoria.nome.asc()).all()

    if request.method == "POST":
        titulo = texto_limpo("titulo")
        descricao = texto_limpo("descricao")
        nivel = texto_limpo("nivel")
        categoria_id = request.form.get("categoria_id", type=int)

        if not titulo or not descricao or not nivel or not categoria_id:
            flash("Preencha titulo, descricao, nivel e categoria.")
            return render_template("curso_form.html", categorias=categorias)

        curso = Curso(
            titulo=titulo,
            descricao=descricao,
            instrutor_id=current_user.id,
            categoria_id=categoria_id,
            nivel=nivel,
        )
        db.session.add(curso)
        db.session.commit()

        flash("Curso criado com sucesso.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    return render_template("curso_form.html", categorias=categorias)


@app.route("/curso/<int:curso_id>")
def detalhe_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    modulos = Modulo.query.filter_by(curso_id=curso.id).order_by(Modulo.ordem.asc()).all()
    matriculado = False
    avaliacao_usuario = None

    if current_user.is_authenticated and current_user.tipo == "aluno":
        matriculado = usuario_ja_matriculado(current_user.id, curso.id)
        avaliacao_usuario = Avaliacao.query.filter_by(usuario_id=current_user.id, curso_id=curso.id).first()

    return render_template(
        "curso_detalhe.html",
        curso=curso,
        modulos=modulos,
        matriculado=matriculado,
        avaliacao_usuario=avaliacao_usuario,
    )


@app.route("/curso/<int:curso_id>/matricular", methods=["POST"])
@login_required
def matricular(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if current_user.tipo != "aluno":
        flash("Somente alunos podem se matricular.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    if usuario_ja_matriculado(current_user.id, curso.id):
        flash("Voce ja esta matriculado neste curso.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    db.session.add(Matricula(usuario_id=current_user.id, curso_id=curso.id))
    db.session.commit()
    flash("Matricula realizada com sucesso.")
    return redirect(url_for("dashboard"))


@app.route("/curso/<int:curso_id>/modulo/novo", methods=["POST"])
@login_required
def novo_modulo(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    if current_user.id != curso.instrutor_id:
        flash("Somente o instrutor deste curso pode adicionar modulos.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    titulo = texto_limpo("titulo")
    ordem = request.form.get("ordem", type=int) or 1

    if not titulo:
        flash("Informe o titulo do modulo.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    modulo = Modulo(curso_id=curso.id, titulo=titulo, ordem=ordem)
    db.session.add(modulo)
    db.session.commit()
    flash("Modulo criado com sucesso.")
    return redirect(url_for("detalhe_curso", curso_id=curso.id))


@app.route("/modulo/<int:modulo_id>/aula/nova", methods=["POST"])
@login_required
def nova_aula(modulo_id):
    modulo = Modulo.query.get_or_404(modulo_id)
    curso = modulo.curso

    if current_user.id != curso.instrutor_id:
        flash("Somente o instrutor deste curso pode adicionar aulas.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    titulo = texto_limpo("titulo")
    tipo_conteudo = texto_limpo("tipo_conteudo")
    url_conteudo = texto_limpo("url_conteudo")
    duracao_minutos = request.form.get("duracao_minutos", type=int) or 0
    ordem = request.form.get("ordem", type=int) or 1

    if not titulo or not tipo_conteudo or not url_conteudo:
        flash("Preencha titulo, tipo de conteudo e URL da aula.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    aula = Aula(
        modulo_id=modulo.id,
        titulo=titulo,
        tipo_conteudo=tipo_conteudo,
        url_conteudo=url_conteudo,
        duracao_minutos=duracao_minutos,
        ordem=ordem,
    )
    db.session.add(aula)
    atualizar_estatisticas_curso(curso)
    db.session.commit()

    flash("Aula adicionada com sucesso.")
    return redirect(url_for("detalhe_curso", curso_id=curso.id))


@app.route("/aula/<int:aula_id>/concluir", methods=["POST"])
@login_required
def concluir_aula(aula_id):
    aula = Aula.query.get_or_404(aula_id)
    curso = aula.modulo.curso

    if current_user.tipo != "aluno":
        flash("Somente alunos podem registrar progresso.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    if not usuario_ja_matriculado(current_user.id, curso.id):
        flash("Voce precisa estar matriculado para concluir aulas.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    progresso = ProgressoAula.query.filter_by(usuario_id=current_user.id, aula_id=aula.id).first()
    if progresso is None:
        progresso = ProgressoAula(
            usuario_id=current_user.id,
            aula_id=aula.id,
            data_conclusao=datetime.utcnow(),
            status="Concluido",
        )
        db.session.add(progresso)
    else:
        progresso.status = "Concluido"
        progresso.data_conclusao = datetime.utcnow()

    concluir_curso_se_necessario(current_user.id, curso)
    db.session.commit()

    flash("Progresso da aula atualizado.")
    return redirect(url_for("detalhe_curso", curso_id=curso.id))


@app.route("/curso/<int:curso_id>/avaliar", methods=["POST"])
@login_required
def avaliar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)

    if current_user.tipo != "aluno":
        flash("Somente alunos podem avaliar cursos.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    if not usuario_ja_matriculado(current_user.id, curso.id):
        flash("Voce precisa estar matriculado para avaliar.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    nota = request.form.get("nota", type=int)
    comentario = texto_limpo("comentario")

    if nota is None or nota < 1 or nota > 5:
        flash("A nota precisa estar entre 1 e 5.")
        return redirect(url_for("detalhe_curso", curso_id=curso.id))

    avaliacao = Avaliacao.query.filter_by(usuario_id=current_user.id, curso_id=curso.id).first()
    if avaliacao is None:
        avaliacao = Avaliacao(
            usuario_id=current_user.id,
            curso_id=curso.id,
            nota=nota,
            comentario=comentario or None,
            data_avaliacao=datetime.utcnow(),
        )
        db.session.add(avaliacao)
    else:
        avaliacao.nota = nota
        avaliacao.comentario = comentario or None
        avaliacao.data_avaliacao = datetime.utcnow()

    db.session.commit()
    flash("Avaliacao salva com sucesso.")
    return redirect(url_for("detalhe_curso", curso_id=curso.id))


@app.route("/plano/<int:plano_id>/assinar", methods=["POST"])
@login_required
def assinar_plano(plano_id):
    plano = Plano.query.get_or_404(plano_id)
    data_inicio = datetime.utcnow().date()
    data_fim = data_inicio + timedelta(days=30 * plano.duracao_meses)

    assinatura = Assinatura(
        usuario_id=current_user.id,
        plano_id=plano.id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    db.session.add(assinatura)
    db.session.flush()

    pagamento = Pagamento(
        assinatura_id=assinatura.id,
        valor_pago=plano.preco,
        metodo_pagamento="Cartao",
        id_transacao_gateway=f"TRX-{uuid4().hex[:12].upper()}",
        data_fim=data_fim,
    )
    db.session.add(pagamento)
    db.session.commit()

    flash("Assinatura criada com pagamento registrado.")
    return redirect(url_for("dashboard"))


@app.route("/popular-demo")
def popular_demo():
    if Usuario.query.count() > 0:
        flash("A base ja possui dados. Se quiser recriar, apague o banco e rode de novo.")
        return redirect(url_for("index"))

    categoria_prog = Categoria(nome="Programacao", descricao="Cursos de desenvolvimento e software.")
    categoria_dados = Categoria(nome="Banco de Dados", descricao="Cursos de modelagem e consultas.")
    categoria_arquitetura = Categoria(
        nome="Arquitetura de Software",
        descricao="Boas praticas, engenharia, qualidade e construcao de software.",
    )
    db.session.add_all([categoria_prog, categoria_dados, categoria_arquitetura])

    professor_daniel = Usuario(
        nome_completo="Professor Daniel",
        email="daniel@cursos.com",
        tipo="instrutor",
    )
    professor_daniel.set_senha("123456")

    instrutora_ana = Usuario(nome_completo="Ana Souza", email="ana@cursos.com", tipo="instrutor")
    instrutora_ana.set_senha("123456")

    instrutor_bruno = Usuario(nome_completo="Bruno Martins", email="bruno@cursos.com", tipo="instrutor")
    instrutor_bruno.set_senha("123456")

    aluno_carlos = Usuario(nome_completo="Carlos Lima", email="carlos@cursos.com", tipo="aluno")
    aluno_carlos.set_senha("123456")

    aluna_marina = Usuario(nome_completo="Marina Alves", email="marina@cursos.com", tipo="aluno")
    aluna_marina.set_senha("123456")

    aluno_joao = Usuario(nome_completo="Joao Pedro", email="joao@cursos.com", tipo="aluno")
    aluno_joao.set_senha("123456")

    db.session.add_all(
        [
            professor_daniel,
            instrutora_ana,
            instrutor_bruno,
            aluno_carlos,
            aluna_marina,
            aluno_joao,
        ]
    )
    db.session.flush()

    curso_tcs = Curso(
        titulo="Tecnologia de Construcao de Software",
        descricao="Curso do Professor Daniel com foco em modelagem, arquitetura, padroes, qualidade e entrega continua.",
        instrutor_id=professor_daniel.id,
        categoria_id=categoria_arquitetura.id,
        nivel="Intermediario",
    )
    curso_python = Curso(
        titulo="Python do Zero ao Projeto",
        descricao="Aprenda logica, funcoes, listas, dicionarios e crie uma aplicacao web simples.",
        instrutor_id=instrutora_ana.id,
        categoria_id=categoria_prog.id,
        nivel="Iniciante",
    )
    curso_sql = Curso(
        titulo="SQL para Banco de Dados",
        descricao="Modele tabelas, relacoes, consultas e normalize seu banco de dados.",
        instrutor_id=instrutor_bruno.id,
        categoria_id=categoria_dados.id,
        nivel="Intermediario",
    )
    curso_api = Curso(
        titulo="APIs REST com Flask",
        descricao="Construa APIs REST, validacao, autenticacao e integracao com banco de dados.",
        instrutor_id=instrutora_ana.id,
        categoria_id=categoria_prog.id,
        nivel="Avancado",
    )
    db.session.add_all([curso_tcs, curso_python, curso_sql, curso_api])
    db.session.flush()

    modulo_tcs_1 = Modulo(curso_id=curso_tcs.id, titulo="Fundamentos da Construcao de Software", ordem=1)
    modulo_tcs_2 = Modulo(curso_id=curso_tcs.id, titulo="Qualidade e Evolucao", ordem=2)
    modulo_python = Modulo(curso_id=curso_python.id, titulo="Fundamentos", ordem=1)
    modulo_sql = Modulo(curso_id=curso_sql.id, titulo="Modelagem Relacional", ordem=1)
    modulo_api = Modulo(curso_id=curso_api.id, titulo="Flask para APIs", ordem=1)
    db.session.add_all([modulo_tcs_1, modulo_tcs_2, modulo_python, modulo_sql, modulo_api])
    db.session.flush()

    db.session.add_all(
        [
            Aula(
                modulo_id=modulo_tcs_1.id,
                titulo="Introducao a Tecnologia de Construcao de Software",
                tipo_conteudo="Video",
                url_conteudo="https://example.com/tcs-introducao",
                duracao_minutos=45,
                ordem=1,
            ),
            Aula(
                modulo_id=modulo_tcs_1.id,
                titulo="Levantamento de requisitos e modelagem",
                tipo_conteudo="Texto",
                url_conteudo="https://example.com/tcs-requisitos",
                duracao_minutos=30,
                ordem=2,
            ),
            Aula(
                modulo_id=modulo_tcs_2.id,
                titulo="Testes, refatoracao e entrega continua",
                tipo_conteudo="Video",
                url_conteudo="https://example.com/tcs-qualidade",
                duracao_minutos=50,
                ordem=1,
            ),
            Aula(
                modulo_id=modulo_python.id,
                titulo="Introducao ao Python",
                tipo_conteudo="Video",
                url_conteudo="https://example.com/python-introducao",
                duracao_minutos=35,
                ordem=1,
            ),
            Aula(
                modulo_id=modulo_python.id,
                titulo="Estruturas de repeticao",
                tipo_conteudo="Texto",
                url_conteudo="https://example.com/python-loops",
                duracao_minutos=28,
                ordem=2,
            ),
            Aula(
                modulo_id=modulo_sql.id,
                titulo="Modelo relacional",
                tipo_conteudo="Video",
                url_conteudo="https://example.com/sql-modelo-relacional",
                duracao_minutos=42,
                ordem=1,
            ),
            Aula(
                modulo_id=modulo_api.id,
                titulo="Criando rotas e respostas JSON",
                tipo_conteudo="Video",
                url_conteudo="https://example.com/flask-api-json",
                duracao_minutos=38,
                ordem=1,
            ),
        ]
    )

    trilha_backend = Trilha(
        titulo="Trilha Back-end",
        descricao="Sequencia sugerida para entrar em desenvolvimento back-end.",
        categoria_id=categoria_prog.id,
    )
    trilha_engenharia = Trilha(
        titulo="Trilha Engenharia de Software",
        descricao="Formacao com foco em construcao, qualidade e manutencao de software.",
        categoria_id=categoria_arquitetura.id,
    )
    db.session.add_all([trilha_backend, trilha_engenharia])
    db.session.flush()

    db.session.add_all(
        [
            TrilhaCurso(trilha_id=trilha_backend.id, curso_id=curso_python.id, ordem=1),
            TrilhaCurso(trilha_id=trilha_backend.id, curso_id=curso_sql.id, ordem=2),
            TrilhaCurso(trilha_id=trilha_backend.id, curso_id=curso_api.id, ordem=3),
            TrilhaCurso(trilha_id=trilha_engenharia.id, curso_id=curso_tcs.id, ordem=1),
            TrilhaCurso(trilha_id=trilha_engenharia.id, curso_id=curso_api.id, ordem=2),
        ]
    )

    plano_basico = Plano(
        nome="Plano Basico",
        descricao="Acesso aos cursos introdutorios e trilhas iniciais.",
        preco=29.9,
        duracao_meses=1,
    )
    plano_pro = Plano(
        nome="Plano Pro",
        descricao="Acesso a todos os cursos e trilhas.",
        preco=49.9,
        duracao_meses=1,
    )
    plano_anual = Plano(
        nome="Plano Anual",
        descricao="Acesso completo por 12 meses com melhor custo-beneficio.",
        preco=499.9,
        duracao_meses=12,
    )
    db.session.add_all([plano_basico, plano_pro, plano_anual])
    db.session.flush()

    assinatura_carlos = Assinatura(
        usuario_id=aluno_carlos.id,
        plano_id=plano_pro.id,
        data_inicio=datetime.utcnow().date(),
        data_fim=(datetime.utcnow() + timedelta(days=30)).date(),
    )
    assinatura_marina = Assinatura(
        usuario_id=aluna_marina.id,
        plano_id=plano_basico.id,
        data_inicio=datetime.utcnow().date(),
        data_fim=(datetime.utcnow() + timedelta(days=30)).date(),
    )
    assinatura_joao = Assinatura(
        usuario_id=aluno_joao.id,
        plano_id=plano_anual.id,
        data_inicio=datetime.utcnow().date(),
        data_fim=(datetime.utcnow() + timedelta(days=365)).date(),
    )
    db.session.add_all([assinatura_carlos, assinatura_marina, assinatura_joao])
    db.session.flush()

    db.session.add_all(
        [
            Pagamento(
                assinatura_id=assinatura_carlos.id,
                valor_pago=plano_pro.preco,
                metodo_pagamento="Cartao de Credito",
                id_transacao_gateway=f"TRX-{uuid4().hex[:12].upper()}",
                data_fim=assinatura_carlos.data_fim,
            ),
            Pagamento(
                assinatura_id=assinatura_marina.id,
                valor_pago=plano_basico.preco,
                metodo_pagamento="PIX",
                id_transacao_gateway=f"TRX-{uuid4().hex[:12].upper()}",
                data_fim=assinatura_marina.data_fim,
            ),
            Pagamento(
                assinatura_id=assinatura_joao.id,
                valor_pago=plano_anual.preco,
                metodo_pagamento="Boleto",
                id_transacao_gateway=f"TRX-{uuid4().hex[:12].upper()}",
                data_fim=assinatura_joao.data_fim,
            ),
        ]
    )

    db.session.add_all(
        [
            Matricula(usuario_id=aluno_carlos.id, curso_id=curso_python.id),
            Matricula(usuario_id=aluno_carlos.id, curso_id=curso_tcs.id),
            Matricula(usuario_id=aluna_marina.id, curso_id=curso_sql.id),
            Matricula(usuario_id=aluno_joao.id, curso_id=curso_api.id),
            Matricula(usuario_id=aluno_joao.id, curso_id=curso_tcs.id),
        ]
    )

    db.session.add(
        Avaliacao(
            usuario_id=aluno_carlos.id,
            curso_id=curso_tcs.id,
            nota=5,
            comentario="Excelente curso do Professor Daniel, muito claro e bem estruturado.",
        )
    )
    db.session.add(
        Avaliacao(
            usuario_id=aluna_marina.id,
            curso_id=curso_sql.id,
            nota=4,
            comentario="Curso muito bom para entender modelagem e consultas.",
        )
    )

    atualizar_estatisticas_curso(curso_python)
    atualizar_estatisticas_curso(curso_sql)
    atualizar_estatisticas_curso(curso_tcs)
    atualizar_estatisticas_curso(curso_api)
    db.session.commit()

    flash("Dados demo criados com Professor Daniel, trilhas, planos, alunos e pagamentos.")
    return redirect(url_for("index"))


@app.route("/init-db")
def init_db():
    db.create_all()
    flash("Banco inicializado com sucesso.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
