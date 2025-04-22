from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100), nullable=False)
    procedimento = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    produtos_utilizados = db.Column(db.String(200), nullable=True)
    custo_produtos = db.Column(db.Float, nullable=True)

    def lucro(self):
        return self.valor - (self.custo_produtos or 0)

@app.route('/')
def index():
    servicos = Servico.query.all()
    return render_template('index.html', servicos=servicos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    cliente = request.form['cliente']
    procedimento = request.form['procedimento']
    valor = float(request.form['valor'])
    produtos = request.form['produtos']
    custo = float(request.form['custo'])

    novo_servico = Servico(
        cliente=cliente,
        procedimento=procedimento,
        valor=valor,
        produtos_utilizados=produtos,
        custo_produtos=custo
    )
    db.session.add(novo_servico)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    servico = Servico.query.get_or_404(id)
    db.session.delete(servico)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Criar o banco de dados e tabelas antes de rodar o app
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
