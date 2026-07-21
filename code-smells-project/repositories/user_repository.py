from database import get_db


_PUBLIC_USER_COLUMNS = "id, nome, email, tipo, criado_em"


def _to_public_user(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def list_users():
    cursor = get_db().execute(f"SELECT {_PUBLIC_USER_COLUMNS} FROM usuarios")
    return [_to_public_user(row) for row in cursor.fetchall()]


def get_user(user_id):
    cursor = get_db().execute(
        f"SELECT {_PUBLIC_USER_COLUMNS} FROM usuarios WHERE id = ?", (user_id,)
    )
    return _to_public_user(cursor.fetchone())


def get_user_for_auth(email):
    cursor = get_db().execute(
        "SELECT id, nome, email, senha, tipo, criado_em FROM usuarios WHERE email = ?",
        (email,),
    )
    return cursor.fetchone()


def list_users_with_passwords():
    cursor = get_db().execute("SELECT id, senha FROM usuarios")
    return cursor.fetchall()


def update_password(user_id, password_hash):
    db = get_db()
    db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (password_hash, user_id))
    db.commit()


def create_user(nome, email, password_hash, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, password_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid
