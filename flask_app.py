from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    nome        = StringField('Informe o seu nome'                  , validators=[DataRequired()])
    sobrenome   = StringField('Informe o seu sobrenome:'            , validators=[DataRequired()])
    instituicao = StringField('Informe a sua Instituição de ensino:', validators=[DataRequired()])
    disciplina  = SelectField('Informe a sua disciplina:'           , choices=[('DSWA5', 'DSWA5'), ('DWBA4', 'DWBA4'), ('Gestão de projetos', 'Gestão de projetos')])
    submit      = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    remote_addr = request.remote_addr;
    remote_host = request.host;
    form        = NameForm()
    if form.validate_on_submit():
        old_name = session.get('nome')
        if old_name is not None and old_name != form.nome.data:
            flash('Você alterou o seu nome!')
        session['name']        = form.nome.data
        session['sobrenome']   = form.sobrenome.data
        session['instituicao'] = form.instituicao.data
        session['disciplina']  = form.disciplina.data
        return redirect(url_for('index'))
    return render_template('index.html',
                            current_time = datetime.utcnow(),
                            form         = form,
                            nome         = session.get('name'),
                            sobrenome    = session.get('sobrenome'),
                            instituicao  = session.get('instituicao'),
                            disciplina   = session.get('disciplina'),
                            remote_addr  = remote_addr,
                            remote_host  = remote_host)















