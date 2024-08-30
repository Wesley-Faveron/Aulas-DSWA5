import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    professores = db.relationship('Professor', backref='disciplina', lazy='dynamic')

    def __repr__(self):
        return '<Disciplina %r>' % self.name

class Professor(db.Model):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, index=True)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id'))

    def __repr__(self):
        return '<Professor %r>' % self.nome

class NameForm(FlaskForm):
    name = StringField('Cadastre o novo Professor:', validators=[DataRequired()])
    role = SelectField(u'Disciplina associada:', coerce=int)
    submit = SubmitField('Cadastrar')

    def __init__(self, *args, **kwargs):
        super(NameForm, self).__init__(*args, **kwargs)
        self.role.choices = [(disciplina.id, disciplina.name) for disciplina in Disciplina.query.order_by(Disciplina.name).all()]

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Professor=Professor, Disciplina=Disciplina)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    current_time = datetime.utcnow()
    return render_template('index.html', current_time=current_time)

    
@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    return render_template('NaoDis.html')
    
@app.route('/alunos', methods=['GET', 'POST'])
def alunos():
    return render_template('NaoDis.html')

@app.route('/professores', methods=['GET', 'POST'])
def professores():
    form = NameForm()
    professores_all = Professor.query.all()
    disciplinas_all = Disciplina.query.all()
    if form.validate_on_submit():
        professor = Professor.query.filter_by(nome=form.name.data).first()
        if professor is None:
            disciplina_associada = Disciplina.query.get(form.role.data)
            professor = Professor(nome=form.name.data, disciplina=disciplina_associada)
            db.session.add(professor)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('professores'))
    return render_template('professores.html', form=form, name=session.get('name'),
                           known=session.get('known', False),
                           professores_all=professores_all, disciplinas_all=disciplinas_all)

def create_disciplines():
    disciplinas = ['DSWA5', 'GPSA5', 'IHCA5', 'SODA5', 'PJIA5', 'TCOA5']
    for nome in disciplinas:
        if not Disciplina.query.filter_by(name=nome).first():
            db.session.add(Disciplina(name=nome))
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        create_disciplines()
    app.run(debug=True)
