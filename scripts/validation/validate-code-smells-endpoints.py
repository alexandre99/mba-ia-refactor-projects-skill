import os
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2] / "code-smells-project"
sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("DATABASE_PATH", ":memory:")
os.environ.setdefault("ADMIN_TOKEN", "validation-token")
os.environ.setdefault("SEED_ADMIN_PASSWORD", "admin123")
os.environ.setdefault("APP_ENV", "test")

from app import app  # noqa: E402
from database import get_db  # noqa: E402
from werkzeug.security import check_password_hash  # noqa: E402


client = app.test_client()


def call(method, path, expected, **kwargs):
    response = client.open(path, method=method, **kwargs)
    assert response.status_code == expected, (
        method,
        path,
        response.status_code,
        response.get_data(as_text=True),
    )
    return response.get_json()


assert call("GET", "/", 200)["versao"] == "1.0.0"
health = call("GET", "/health", 200)
assert {"secret_key", "debug", "db_path"}.isdisjoint(health)
assert len(call("GET", "/produtos", 200)["dados"]) == 10
assert call("GET", "/produtos/busca?q=Mouse", 200)["total"] == 1
assert "dados" in call("GET", "/produtos/1", 200)

created = call(
    "POST",
    "/produtos",
    201,
    json={
        "nome": "Validation Produto",
        "descricao": "desc",
        "preco": 10.5,
        "estoque": 3,
        "categoria": "geral",
    },
)
product_id = created["dados"]["id"]
call(
    "PUT",
    f"/produtos/{product_id}",
    200,
    json={
        "nome": "Validation Atualizado",
        "descricao": "desc2",
        "preco": 12.5,
        "estoque": 4,
        "categoria": "geral",
    },
)
call("DELETE", f"/produtos/{product_id}", 200)
call("GET", f"/produtos/{product_id}", 404)

assert all("senha" not in user for user in call("GET", "/usuarios", 200)["dados"])
assert "senha" not in call("GET", "/usuarios/1", 200)["dados"]
call("GET", "/usuarios/9999", 404)
new_user = call(
    "POST",
    "/usuarios",
    201,
    json={"nome": "Validation User", "email": "validation@example.com", "senha": "validation-pass"},
)
stored_password = get_db().execute(
    "SELECT senha FROM usuarios WHERE id = ?", (new_user["dados"]["id"],)
).fetchone()["senha"]
assert check_password_hash(stored_password, "validation-pass")
call("POST", "/login", 200, json={"email": "admin@loja.com", "senha": "admin123"})
call("POST", "/login", 401, json={"email": "admin@loja.com", "senha": "wrong-password"})
call("POST", "/login", 200, json={"email": "validation@example.com", "senha": "validation-pass"})

call("POST", "/pedidos", 201, json={"usuario_id": 1, "itens": [{"produto_id": 2, "quantidade": 1}]})
assert len(call("GET", "/pedidos", 200)["dados"]) == 1
assert len(call("GET", "/pedidos/usuario/1", 200)["dados"]) == 1
call("PUT", "/pedidos/1/status", 200, json={"status": "aprovado"})
assert "faturamento_bruto" in call("GET", "/relatorios/vendas", 200)["dados"]

assert call(
    "POST",
    "/admin/query",
    200,
    json={"sql": "SELECT COUNT(*) AS total FROM produtos"},
)["dados"][0]["total"] == 10
call("POST", "/admin/query", 400, json={"sql": "DELETE FROM produtos"})
call("POST", "/admin/query", 400, json={"sql": "DROP TABLE produtos"})
health_before_reset = call("GET", "/health", 200)
call("POST", "/admin/reset-db", 403)
assert call("GET", "/health", 200)["counts"] == health_before_reset["counts"]
call("POST", "/admin/reset-db", 200, headers={"X-Admin-Token": "validation-token"})
assert call("GET", "/health", 200)["counts"] == {"produtos": 0, "usuarios": 0, "pedidos": 0}

print("code-smells-project endpoint validation passed: 19 original paths plus security probes")
