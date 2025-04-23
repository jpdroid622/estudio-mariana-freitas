
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# Simulando banco de dados Firebase (substituir depois por integração real)
db = {
    'servicos': {},
    'produtos': {},
    'agendamentos': {},
    'execucoes': {},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/servicos')
def listar_servicos():
    return render_template('servicos.html', servicos=db['servicos'])

@app.route('/servicos/adicionar', methods=['POST'])
def adicionar_servico():
    id_servico = str(uuid.uuid4())
    db['servicos'][id_servico] = {
        'nome': request.form['nome'],
        'descricao': request.form['descricao'],
        'preco': float(request.form['preco']),
        'duracao': request.form['duracao']
    }
    return redirect(url_for('listar_servicos'))

@app.route('/produtos')
def listar_produtos():
    return render_template('produtos.html', produtos=db['produtos'])

@app.route('/produtos/adicionar', methods=['POST'])
def adicionar_produto():
    id_produto = str(uuid.uuid4())
    db['produtos'][id_produto] = {
        'nome': request.form['nome'],
        'quantidade': float(request.form['quantidade']),
        'preco': float(request.form['preco'])
    }
    return redirect(url_for('listar_produtos'))

@app.route('/agendamentos')
def listar_agendamentos():
    return render_template('agendamentos.html', agendamentos=db['agendamentos'])

@app.route('/agendamentos/adicionar', methods=['POST'])
def adicionar_agendamento():
    id_agendamento = str(uuid.uuid4())
    db['agendamentos'][id_agendamento] = {
        'cliente': request.form['cliente'],
        'telefone': request.form['telefone'],
        'servico': request.form['servico'],
        'data_hora': request.form['data_hora']
    }
    return redirect(url_for('listar_agendamentos'))

@app.route('/execucoes')
def listar_execucoes():
    return render_template('execucoes.html', execucoes=db['execucoes'])

@app.route('/execucoes/adicionar', methods=['POST'])
def adicionar_execucao():
    id_execucao = str(uuid.uuid4())
    servico = db['servicos'][request.form['servico']]
    produto_id = request.form['produto']
    quantidade_usada = float(request.form['quantidade_usada'])
    produto = db['produtos'][produto_id]

    custo = (produto['preco'] / 1.0) * quantidade_usada
    lucro = servico['preco'] - custo

    db['produtos'][produto_id]['quantidade'] -= quantidade_usada

    db['execucoes'][id_execucao] = {
        'servico': servico['nome'],
        'produto': produto['nome'],
        'quantidade_usada': quantidade_usada,
        'custo': custo,
        'lucro': lucro,
        'data': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    return redirect(url_for('listar_execucoes'))

@app.route('/relatorios')
def relatorios():
    total_lucro = sum(e['lucro'] for e in db['execucoes'].values())
    total_custo = sum(e['custo'] for e in db['execucoes'].values())
    media_lucro = total_lucro / len(db['execucoes']) if db['execucoes'] else 0
    estoque_baixo = {k: v for k, v in db['produtos'].items() if v['quantidade'] < 5}
    return render_template('relatorios.html', lucro=total_lucro, custo=total_custo, media=media_lucro, estoque=estoque_baixo)

if __name__ == '__main__':
    app.run(debug=True)
