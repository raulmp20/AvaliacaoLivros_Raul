from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os

app = Flask(__name__)

# Definindo as variáveis de ambiente
API_BASE_URL = "http://backend:8000"


# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')


# Rota para exibir o formulário de cadastro
@app.route('/cadastro', methods=['GET'])
def inserir_mercadoria_form():
    return render_template('cadastro.html')


# Rota para enviar os dados do formulário de cadastro para a API
@app.route('/inserir', methods=['POST'])
def inserir_mercadoria():
    nome = request.form['nome']
    quantidade = request.form['quantidade']
    preco = request.form['preco']

    payload = {
        'nome': nome,
        'quantidade': quantidade,
        'preco': preco
    }

    response = requests.post(f'{API_BASE_URL}/api/v1/mercadorias/', json=payload)

    if response.status_code == 201:
        return redirect(url_for('listar_mercadorias'))
    else:
        return "Erro ao inserir mercadoria", 500


# Rota para listar todas as mercadorias
@app.route('/estoque', methods=['GET'])
def listar_mercadorias():
    response = requests.get(f'{API_BASE_URL}/api/v1/mercadorias/')
    try:
        mercadorias = response.json()
    except:
        mercadorias = []
    return render_template('estoque.html', mercadorias=mercadorias)


# Rota para exibir o formulário de edição de mercadoria
@app.route('/atualizar/<int:mercadoria_codigo>', methods=['GET'])
def atualizar_mercadoria_form(mercadoria_codigo):
    response = requests.get(f"{API_BASE_URL}/api/v1/mercadorias/")
    # filtrando apenas a mercadoria correspondente ao Codigo
    mercadorias = [mercadoria for mercadoria in response.json() if mercadoria['codigo'] == mercadoria_codigo]
    if len(mercadorias) == 0:
        return "mercadoria não encontrada", 404
    mercadoria = mercadorias[0]
    return render_template('atualizar.html', mercadoria=mercadoria)


# Rota para enviar os dados do formulário de edição de mercadoria para a API
@app.route('/atualizar/<int:mercadoria_codigo>', methods=['POST'])
def atualizar_mercadoria(mercadoria_codigo):
    nome = request.form['nome']
    quantidade = request.form['quantidade']
    preco = request.form['preco']

    payload = {
        'codigo': mercadoria_codigo,
        'nome': nome,
        'quantidade': quantidade,
        'preco': preco
    }

    response = requests.patch(f"{API_BASE_URL}/api/v1/mercadorias/{mercadoria_codigo}", json=payload)

    if response.status_code == 200:
        return redirect(url_for('listar_mercadorias'))
    else:
        return "Erro ao atualizar mercadoria", 500


# Rota para exibir o formulário de edição de mercadoria
@app.route('/vender/<int:mercadoria_codigo>', methods=['GET'])
def vender_mercadoria_form(mercadoria_codigo):
    response = requests.get(f"{API_BASE_URL}/api/v1/mercadorias/")
    # filtrando apenas a mercadoria correspondente ao Codigo
    mercadorias = [mercadoria for mercadoria in response.json() if mercadoria['codigo'] == mercadoria_codigo]
    if len(mercadorias) == 0:
        return "mercadoria não encontrada", 404
    mercadoria = mercadorias[0]
    return render_template('vender.html', mercadoria=mercadoria)


# Rota para vender uma mercadoria
@app.route('/vender/<int:mercadoria_codigo>', methods=['POST'])
def vender_mercadoria(mercadoria_codigo):
    quantidade = request.form['quantidade']

    payload = {
        'quantidade': quantidade
    }

    response = requests.put(f"{API_BASE_URL}/api/v1/mercadorias/{mercadoria_codigo}/vender/", json=payload)

    if response.status_code == 200:
        return redirect(url_for('listar_mercadorias'))
    else:
        return "Erro ao vender mercadoria", 500


# Rota para listar todas as vendas
@app.route('/vendas', methods=['GET'])
def listar_vendas():
    response = requests.get(f"{API_BASE_URL}/api/v1/vendas/")
    try:
        vendas = response.json()
    except:
        vendas = []
    # salvando nomes das mercadorias vendidas
    total_vendas = 0
    for venda in vendas:
        total_vendas += float(venda['valor_venda'])
    return render_template('vendas.html', vendas=vendas, total_vendas=total_vendas)


# Rota para excluir uma mercadoria
@app.route('/excluir/<int:mercadoria_codigo>', methods=['POST'])
def excluir_mercadoria(mercadoria_codigo):
    response = requests.delete(f"{API_BASE_URL}/api/v1/mercadorias/{mercadoria_codigo}")

    if response.status_code == 200:
        return redirect(url_for('listar_mercadorias'))
    else:
        return "Erro ao excluir mercadorias", 500


# Rota para resetar o database
@app.route('/reset-database', methods=['GET'])
def resetar_database():
    response = requests.delete(f"{API_BASE_URL}/api/v1/mercadorias/")

    if response.status_code == 200:
        return render_template('confirmacao.html')
    else:
        return "Erro ao resetar o database", 500


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
