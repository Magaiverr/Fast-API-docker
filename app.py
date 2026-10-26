from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from pathlib import Path
import sqlite3
import secrets

app = FastAPI()

security = HTTPBasic()

USUARIO_CORRETO = "murilo"
SENHA_CORRETA = "123456"

CAMINHO_BANCO = Path(__file__).resolve().parent / "tarefas.db"


class Tarefa(BaseModel):
    nome: str
    descricao: str
    concluida: bool = False


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    with conectar_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                concluida INTEGER NOT NULL DEFAULT 0
            )
        """)


criar_tabela()


def converter_tarefa(registro):
    return {
        "id": registro["id"],
        "nome": registro["nome"],
        "descricao": registro["descricao"],
        "concluida": bool(registro["concluida"])
    }


def autenticar_usuario(
    credenciais: HTTPBasicCredentials = Depends(security)
):
    usuario_correto = secrets.compare_digest(
        credenciais.username.encode("utf-8"),
        USUARIO_CORRETO.encode("utf-8")
    )

    senha_correta = secrets.compare_digest(
        credenciais.password.encode("utf-8"),
        SENHA_CORRETA.encode("utf-8")
    )

    if not (usuario_correto and senha_correta):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )

    return credenciais.username


@app.post("/tarefas", dependencies=[Depends(autenticar_usuario)])
def adicionar_tarefa(tarefa: Tarefa):
    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO tarefas (nome, descricao, concluida)
            VALUES (?, ?, ?)
            """,
            (
                tarefa.nome,
                tarefa.descricao,
                int(tarefa.concluida)
            )
        )

        registro = conexao.execute(
            "SELECT * FROM tarefas WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

        return converter_tarefa(registro)


@app.get("/tarefas", dependencies=[Depends(autenticar_usuario)])
def listar_tarefas(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    order_by: str = Query(default="nome")
):
    campos_validos = ["id", "nome", "descricao", "concluida"]

    if order_by not in campos_validos:
        raise HTTPException(
            status_code=400,
            detail=(
                "Campo inválido para ordenação. "
                f"Escolha entre: {campos_validos}"
            )
        )

    inicio = (page - 1) * size

    coluna = (
        "concluida"
        if order_by == "concluida"
        else order_by
    )

    with conectar_banco() as conexao:
        registros = conexao.execute(
            f"""
            SELECT *
            FROM tarefas
            ORDER BY {coluna} ASC
            LIMIT ? OFFSET ?
            """,
            (size, inicio)
        ).fetchall()

        return [
            converter_tarefa(registro)
            for registro in registros
        ]


@app.put(
    "/tarefas/{nome}",
    dependencies=[Depends(autenticar_usuario)]
)
def concluir_tarefa(nome: str):
    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE tarefas
            SET concluida = 1
            WHERE nome = ?
            """,
            (nome,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada"
            )

        registro = conexao.execute(
            """
            SELECT *
            FROM tarefas
            WHERE nome = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (nome,)
        ).fetchone()

        return converter_tarefa(registro)


@app.delete(
    "/tarefas/{nome}",
    dependencies=[Depends(autenticar_usuario)]
)
def remover_tarefa(nome: str):
    with conectar_banco() as conexao:
        cursor = conexao.execute(
            "DELETE FROM tarefas WHERE nome = ?",
            (nome,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada"
            )

        return {
            "mensagem": "Tarefa removida com sucesso"
        }
