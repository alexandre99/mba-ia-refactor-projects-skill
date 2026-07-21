import os
import secrets
import sqlite3

from werkzeug.security import generate_password_hash


_db_connection = None
_configured_path = None


def configure_database(path):
    global _db_connection, _configured_path
    if _configured_path == path:
        return
    close_db()
    _configured_path = path


def _database_path():
    return _configured_path or os.environ.get("DATABASE_PATH", "loja.db")


def get_db():
    global _db_connection
    if _db_connection is None:
        path = _database_path()
        _db_connection = sqlite3.connect(path, check_same_thread=False)
        _db_connection.row_factory = sqlite3.Row
        _create_schema(_db_connection)
        _seed_data(_db_connection)
    return _db_connection


def close_db():
    global _db_connection
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None


def initialize_database():
    db = get_db()
    _upgrade_legacy_passwords(db)
    return db


def _create_schema(db):
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            preco REAL,
            estoque INTEGER,
            categoria TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            senha TEXT,
            tipo TEXT DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            status TEXT DEFAULT 'pendente',
            total REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL
        );
        """
    )
    db.commit()


def _seed_data(db):
    if db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] != 0:
        return

    produtos = [
        ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
        ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
        ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
        ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
        ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
        ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
        ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
        ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
        ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
        ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
    ]
    db.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        produtos,
    )

    admin_password = os.environ.get("SEED_ADMIN_PASSWORD") or secrets.token_urlsafe(24)
    usuarios = [
        ("Admin", "admin@loja.com", generate_password_hash(admin_password), "admin"),
        ("João Silva", "joao@email.com", generate_password_hash(secrets.token_urlsafe(24)), "cliente"),
        ("Maria Santos", "maria@email.com", generate_password_hash(secrets.token_urlsafe(24)), "cliente"),
    ]
    db.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        usuarios,
    )
    db.commit()


def _upgrade_legacy_passwords(db):
    rows = db.execute("SELECT id, senha FROM usuarios").fetchall()
    changed = False
    for row in rows:
        password = row["senha"] or ""
        if not password.startswith(("scrypt:", "pbkdf2:", "argon2:")):
            db.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (generate_password_hash(password), row["id"]),
            )
            changed = True
    if changed:
        db.commit()
