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
def inserir_livro_form():
    return render_template('cadastro.html')


# Rota para enviar os dados do formulário de cadastro para a API
@app.route('/inserir', methods=['POST'])
def inserir_livro():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao =request.form['ano_publicacao']
    editora = request.form['editora']
    status_leitura = request.form['status_leitura'] == 'true'
    nota = request.form['nota']
    nota = int(nota) if nota else None

    payload = {
        'titulo': titulo,
        'autor': autor,
        'ano_publicacao': ano_publicacao,
        'editora': editora,
        'status_leitura': status_leitura,
        'nota': nota
    }

    response = requests.post(f'{API_BASE_URL}/api/v1/livros/', json=payload)

    if response.status_code == 201:
        return redirect(url_for('listar_livros'))
    else:
        return "Erro ao inserir livro", 500



# Rota para listar todos livros
@app.route('/prateleira', methods=['GET'])
def listar_livros():
    response = requests.get(f'{API_BASE_URL}/api/v1/livros/')
    try:
        livros = response.json()
    except:
        livros = []
    return render_template('prateleira.html', livros=livros)


# Rota para exibir o formulário de edição do livro
@app.route('/atualizar/<int:livro_id>', methods=['GET'])
def atualizar_livro_form(livro_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/livros/")
    # filtrando apenas o livro correspondente ao ID
    livros = [livro for livro in response.json() if livro['id'] == livro_id]
    if len(livros) == 0:
        return "livro não encontrado", 404
    livro = livros[0]
    return render_template('atualizar.html', livro=livro)


# Rota para enviar os dados do formulário de edição do livro para a API
@app.route('/atualizar/<int:livro_id>', methods=['POST'])
def atualizar_livro(livro_id):
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']
    editora = request.form['editora']
    status_leitura = request.form['status_leitura']
    nota = request.form['nota']

    payload = {
        'id': livro_id,
        'titulo': titulo,
        'autor': autor,
        'ano_publicacao': ano_publicacao,
        'editora': editora,
        'status_leitura': status_leitura,
        'nota': nota
    }

    response = requests.patch(f"{API_BASE_URL}/api/v1/livros/{livro_id}", json=payload)

    if response.status_code == 200:
        return redirect(url_for('listar_livros'))
    else:
        return "Erro ao atualizar livro", 500


# Rota para exibir o formulário de edição do livro
@app.route('/avaliar/<int:livro_id>', methods=['GET'])
def avaliar_livro_form(livro_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/livros/{livro_id}")
    if response.status_code != 200:
        return "Livro não encontrado", 404

    livro = response.json()
    return render_template('avaliar.html', livro=livro)


# Rota para avaliar um livro
@app.route('/avaliar/<int:livro_id>', methods=['POST'])
def avaliar_livro(livro_id):
    texto_avaliacao = request.form.get('texto_avaliacao')

    if not texto_avaliacao:
        return "O campo 'Texto da Avaliação' é obrigatório.", 400

    # Criar o payload apenas com o campo esperado
    payload = {
        'texto_avaliacao': texto_avaliacao
    }

    # Enviar a requisição PUT para o backend
    response = requests.put(f"{API_BASE_URL}/api/v1/livros/{livro_id}/avaliar/", json=payload)

    # Tratar respostas do backend
    if response.status_code == 200:
        return redirect(url_for('listar_livros'))  # Redirecionar após sucesso
    elif response.status_code == 404:
        return "Livro não encontrado", 404
    else:
        return f"Erro ao avaliar o livro: {response.text}", 500


# Rota para listar todas as avaliacoes
@app.route('/avaliacoes', methods=['GET'])
def listar_avaliacoes():
    response = requests.get(f"{API_BASE_URL}/api/v1/avaliacoes/")
    if response.status_code != 200:
        return "Erro ao obter avaliacoes", 500

    avaliacoes = response.json()

    #Obter títulos usando menos requisições
    livro_ids = {avaliacao.get('livro_id') for avaliacao in avaliacoes}
    livros = {}
    if livro_ids:
        livro_response = requests.get(f"{API_BASE_URL}/api/v1/livros/", params={"ids": ','.join(map(str,livro_ids))})
        if livro_response.status_code == 200:
            livros_data = livro_response.json()
            livros = {livro['id']: livro['titulo'] for livro in livros_data}

    # Adicionar título dos livros ao contexto das avaliações
    avaliacoes_com_titulos = [
        {
            "id": avaliacao['id'],
            "livro_id": avaliacao['livro_id'],
            "texto_avaliacao": avaliacao['texto_avaliacao'],
            "data_avaliacao": avaliacao['data_avaliacao'],
            "titulo": livros.get(avaliacao['livro_id'], 'Título não encontrado')
        }
        for avaliacao in avaliacoes
    ]
    return render_template('avaliacoes.html', avaliacoes=avaliacoes_com_titulos)


# Rota para excluir um livro
@app.route('/excluir/<int:livro_id>', methods=['POST'])
def excluir_livro(livro_id):
    response = requests.delete(f"{API_BASE_URL}/api/v1/livros/{livro_id}")

    if response.status_code == 200:
        return redirect(url_for('listar_livros'))
    else:
        return "Erro ao excluir livro", 500


# Rota para resetar o database
@app.route('/reset-database', methods=['GET'])
def resetar_database():
    response = requests.delete(f"{API_BASE_URL}/api/v1/livros/")

    if response.status_code == 200:
        return render_template('confirmacao.html')
    else:
        return "Erro ao resetar o database", 500


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
