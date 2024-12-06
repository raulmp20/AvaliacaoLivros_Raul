DROP TABLE IF EXISTS "avaliacoes";
DROP TABLE IF EXISTS "livros";

CREATE TABLE "livros" (
    "id" SERIAL PRIMARY KEY,
    "titulo" VARCHAR(255) NOT NULL,
    "autor" VARCHAR(255) NOT NULL,
    "ano_publicacao" INTEGER NOT NULL,
    "editora" VARCHAR(255) NOT NULL,
    "status_leitura" BOOLEAN NOT NULL, -- Status de leitura (true ou false)
    "nota" INTEGER -- Nota do livro (opcional)
);

CREATE TABLE "avaliacoes" (
    "id" SERIAL PRIMARY KEY,
    "livro_id" INTEGER REFERENCES "livros"("id") ON DELETE CASCADE,
    "texto_avaliacao" VARCHAR(1000) NOT NULL,
    "data_avaliacao" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO "livros" ("titulo", "autor", "ano_publicacao", "editora", "status_leitura")
VALUES ('Percy Jackson e o Ladrão de Raios', 'Rick Riordan', 2005, 'Intrinceca', false);

INSERT INTO "livros" ("titulo", "autor", "ano_publicacao", "editora", "status_leitura", "nota")
VALUES ('O Chamado do Cuco', 'Robert Galbraith', 2013, 'Rocco', true, 9);

INSERT INTO "livros" ("titulo", "autor", "ano_publicacao", "editora", "status_leitura", "nota")
VALUES ('Guerra dos Tronos', 'George R.R. Martin', 1996, 'Editora Suma', true, 10);
