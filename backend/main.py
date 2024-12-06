import datetime

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, root_validator
from typing import List, Optional
import time
import asyncpg
import os

# Função para obter a conexão com o banco de dados PostgreSQL
async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgres://postgres:postgres@db:5432/livros")
    try:
        return await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {str(e)}")


# Inicializar a aplicação FastAPI
app = FastAPI()

# Modelo para adicionar novos livros
class Livros(BaseModel):
    id: Optional[int] = None
    titulo: str
    autor: str
    ano_publicacao: int
    editora: str
    status_leitura: bool
    nota: Optional[int] = None

class LivroBase(BaseModel):
    titulo: str
    autor: str
    ano_publicacao: int
    editora: str
    status_leitura: bool = False
    nota: Optional[int] = None

    @root_validator(skip_on_failure=True)
    def validar_nota(cls, values):
        status_leitura = values.get('status_leitura')
        nota = values.get('nota')
        if not status_leitura and nota is not None:
            raise ValueError("Nota só pode ser preenchida se o status de leitura for verdadeiro.")
        return values


# Modelo para avaliacao de Livros
class AvaliacaoLivros(BaseModel):
    texto_avaliacao: str

# Modelo para atualizar atributos de um livro (exceto o codigo)
class AtualizarLivro(BaseModel):
    titulo: Optional[str] = None
    autor: Optional[str] = None
    ano_publicacao: Optional[int] = None
    editora: Optional[str] = None
    status_leitura: Optional[bool] = None
    nota: Optional[int] = None

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Função para verificar se o livro existe usando titulo
async def livro_existe(titulo: str, conn: asyncpg.Connection):
    try:
        query = "SELECT * FROM livros WHERE LOWER(titulo) = LOWER($1)"
        result = await conn.fetchrow(query, titulo)
        return result is not None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao verificar se o livro existe: {str(e)}")

# 1. Adicionar um novo livro
@app.post("/api/v1/livros/", status_code=201)
async def adicionar_livro(livro: LivroBase):
    conn = await get_database()
    if await livro_existe(livro.titulo, conn):
        raise HTTPException(status_code=400, detail="Livro já existe.")
    try:
        query = "INSERT INTO livros (titulo, autor, ano_publicacao, editora, status_leitura, nota) VALUES ($1, $2, $3, $4, $5, $6)"
        async with conn.transaction():
            result = await conn.execute(query, livro.titulo, livro.autor, livro.ano_publicacao, livro.editora, livro.status_leitura, livro.nota if livro.status_leitura else None)
            return {"message": "Livro adicionado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao adicionar o livro: {str(e)}")
    finally:
        await conn.close()

# 2. Listar todos os livros
@app.get("/api/v1/livros/", response_model=List[Livros])
async def listar_livros():
    conn = await get_database()
    try:
        # Buscar todos os livros no banco de dados
        query = "SELECT * FROM livros"
        rows = await conn.fetch(query)
        livros = [dict(row) for row in rows]
        return livros
    finally:
        await conn.close()

# 3. Buscar livro por id
@app.get("/api/v1/livros/{livro_id}")
async def listar_livro_por_id(livro_id: int):
    conn = await get_database()
    try:
        # Buscar o livro por id
        query = "SELECT * FROM livros WHERE id = $1"
        livro = await conn.fetchrow(query, livro_id)
        if livro is None:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")
        return dict(livro)
    finally:
        await conn.close()

# 4. Avaliar um Livro
@app.put("/api/v1/livros/{livro_id}/avaliar/")
async def avaliar_livro(livro_id:int, avaliacao: AvaliacaoLivros):
    conn = await get_database()
    try:
        # Verificar se o livro existe
        livro_query = "SELECT * FROM livros WHERE id = $1"
        livro = await conn.fetchrow(livro_query, livro_id)
        if livro is None:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")


        # Inserir resenha na tabela avaliacao
        inserir_avaliacao_query = """ INSERT INTO avaliacoes (livro_id, texto_avaliacao) VALUES ($1, $2)"""
        await conn.execute(inserir_avaliacao_query, livro_id, avaliacao.texto_avaliacao)


        return {
            "message": "Livro avaliado com sucesso!",
            "dados": dict(avaliacao),
        }
    finally:
        await conn.close()
# 5. Atualizar atributos de um livro pelo id (exceto o id)
@app.patch("/api/v1/livros/{livro_id}")
async def atualizar_livro(livro_id: int, livro_atualizacao: AtualizarLivro):
    conn = await get_database()
    try:
        # Verificar se o livro existe
        query = "SELECT * FROM livros WHERE id = $1"
        livro = await conn.fetchrow(query, livro_id)
        if livro is None:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")

        # Atualizar apenas os campos fornecidos
        update_query = """
            UPDATE livros
            SET titulo = COALESCE($1, titulo),
                autor = COALESCE($2, autor),
                ano_publicacao = COALESCE($3, ano_publicacao),
                editora = COALESCE($4, editora),
                status_leitura = COALESCE($5, status_leitura),
                nota = COALESCE($6, nota)
            WHERE id = $7
        """
        await conn.execute(
            update_query,
            livro_atualizacao.titulo,
            livro_atualizacao.autor,
            livro_atualizacao.ano_publicacao,
            livro_atualizacao.editora,
            livro_atualizacao.status_leitura,
            livro_atualizacao.nota,
            livro_id
        )
        return {"message": "Livro atualizado com sucesso!"}
    finally:
        await conn.close()

# 6. Remover um livro pelo id
@app.delete("/api/v1/livros/{livro_id}")
async def remover_livro(livro_id: int):
    conn = await get_database()
    try:
        # Verificar se o livro existe
        query = "SELECT * FROM livros WHERE id = $1"
        livro = await conn.fetchrow(query, livro_id)
        if livro is None:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")

        # Remover o livro do banco de dados
        delete_query = "DELETE FROM livros WHERE id = $1"
        await conn.execute(delete_query, livro_id)
        return {"message": "Livro removido com sucesso!"}
    finally:
        await conn.close()

# 7. Resetar repositorio de livros
@app.delete("/api/v1/livros/")
async def resetar_livros():
    init_sql = os.getenv("INIT_SQL", "db/init.sql")
    conn = await get_database()
    if not os.path.exists(init_sql):
        raise HTTPException(status_code=500, detail="Arquivo de inicialização não encontrado.")
    try:
        # Read SQL file contents
        with open(init_sql, 'r') as file:
            sql_commands = file.read()
        # Execute SQL commands
        await conn.execute(sql_commands)
        return {"message": "Banco de dados limpo com sucesso!!"}
    finally:
        await conn.close()


# 8 . Listar avaliações
@app.get("/api/v1/avaliacoes/")
async def listar_avaliacoes():
    conn = await get_database()
    try:
        query = """
        SELECT a.id, l.titulo AS livro_titulo, l.nota, a.texto_avaliacao, a.data_avaliacao, a.livro_id
        FROM avaliacoes a
        JOIN livros l ON a.livro_id = l.id
        """
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]
    finally:
        await conn.close()
