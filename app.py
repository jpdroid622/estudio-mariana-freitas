
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    valor = db.Column(db.Float)
    quantidade = db.Column(db.Float)

class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    valor = db.Column(db.Float)
    produtos_usados = db.Column(db.String(500))  # Ex: "shampoo:0.1,creme:0.2"

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    data = db.Column(db.String(20))
    horario = db.Column(db.String(20))

class ExecucaoServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servico_id = db.Column(db.Integer)
    data = db.Column(db.String(20))
    lucro = db.Column(db.Float)

@app.before_first_request
def criar_tabelas():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agendamento', methods=['GET', 'POST'])
def agendamento():
    if request.method == 'POST':
        nome = request.form['nome']
        data = request.form['data']
        horario = request.form['horario']
        novo = Agendamento(nome=nome, data=data, horario=horario)
        db.session.add(novo)
        db.session.commit()
        return redirect('/')
    return render_template('agendamento.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha = request.form['senha']
        if senha == 'admin':
            return redirect('/admin')
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/cadastro-produto', methods=['GET', 'POST'])
def cadastro_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        valor = float(request.form['valor'])
        quantidade = float(request.form['quantidade'])
        novo = Produto(nome=nome, valor=valor, quantidade=quantidade)
        db.session.add(novo)
        db.session.commit()
        return redirect('/admin')
    return render_template('cadastro_produto.html')

@app.route('/cadastro-servico', methods=['GET', 'POST'])
def cadastro_servico():
    if request.method == 'POST':
        nome = request.form['nome']
        valor = float(request.form['valor'])
        produtos_usados = request.form['produtos_usados']
        novo = Servico(nome=nome, valor=valor, produtos_usados=produtos_usados)
        db.session.add(novo)
        db.session.commit()
        return redirect('/admin')
    return render_template('cadastro_servico.html')

@app.route('/executar-servico', methods=['GET', 'POST'])
def executar_servico():
    servicos = Servico.query.all()
    if request.method == 'POST':
        servico_id = int(request.form['servico_id'])
        servico = Servico.query.get(servico_id)
        custo_total = 0.0
        if servico.produtos_usados:
            produtos = servico.produtos_usados.split(',')
            for p in produtos:
                nome, percentual = p.split(':')
                percentual = float(percentual)
                produto = Produto.query.filter_by(nome=nome).first()
                if produto:
                    custo = produto.valor * percentual
                    custo_total += custo
                    produto.quantidade -= percentual
                    if produto.quantidade < 0:
                        produto.quantidade = 0
                    db.session.commit()
        lucro = servico.valor - custo_total
        execucao = ExecucaoServico(servico_id=servico_id, data=str(datetime.today().date()), lucro=lucro)
        db.session.add(execucao)
        db.session.commit()
        return redirect('/admin')
    return render_template('executar_servico.html', servicos=servicos)

@app.route('/relatorio-mensal')
def relatorio_mensal():
    execucoes = ExecucaoServico.query.all()
    produtos = Produto.query.all()
    lucro_total = sum(e.lucro for e in execucoes)
    reposicoes = [p for p in produtos if p.quantidade < 5]
    return render_template('relatorio_mensal.html', execucoes=execucoes, lucro_total=lucro_total, reposicoes=reposicoes)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
