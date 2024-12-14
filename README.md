# Sistema de Avaliação de Livros

## Índice
1. [Explicação](#explicação)
2. [Tecnologias Utilizadas](#tecnologiasutilizadas)
3. [Instruções para Execução](#instrucoesexecucao)

## Explicação

Este projeto tem a intenção de servir como uma rede social para leitores, onde cada usuário pode cadastrar um livro que está lendo, tem a intenção de ler ou já leu. Caso ele já tenho sido lido, o sistema permite que esse livro seja avaliado pelo usuário, primeiramente com uma nota, e depois com uma avaliação em texto. 
A aplicação permite que o usuário veja a lista de livros cadastrados, suas características e a lista de avaliação feitas por ele.

## Tecnologias Utilizadas

- **Backend**: FastAPI (Python)
- **Frontend**: Flask (Python)
- **Banco de Dados**: PostgreSQL
- **Docker**: Para containerizar as aplicações
- **HTML/CSS**: Para o design do frontend
- **Bootstrap**: Para o layout responsivo

## Instruções para Execução

## 1. Pré-requisitos

Certifique-se de que você tenha os seguintes softwares instalados:

- **Docker** e **Docker Compose**: Para rodar a aplicação em containers.
- **Python 3.8+**: Se você preferir rodar a aplicação localmente sem Docker.

## 2. Executando com Docker

O projeto está configurado para ser executado com Docker. Para rodar a aplicação, siga os seguintes passos:

1. Construa e inicie os containers:
```bash
docker-compose up --build
```

2. Acesse a aplicação pelo navegador:
```bash
http://127.0.0.1:3000/
```
