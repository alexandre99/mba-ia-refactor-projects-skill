from repositories import health_repository


def get_health(environment):
    return {
        "status": "ok",
        "database": "connected",
        "counts": health_repository.get_health_counts(),
        "versao": "1.0.0",
        "ambiente": environment,
    }
