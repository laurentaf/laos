"""Start project databases (postgres + redis)."""
import docker
import time
import sys

c = docker.from_env()

# 1. Stop old postgres
for container in c.containers.list():
    if 'postgres' in container.name:
        print(f"Stopping old: {container.name}")
        container.stop()
        container.remove()
        print("  removed")

# 2. Start redis (already running as eixo-redis)
running_names = {c.name for c in c.containers.list()}
if 'eixo-redis' not in running_names:
    print("Starting redis...")
    c.containers.run('redis:7-alpine', name='eixo-redis',
        ports={'6379/tcp': 6379}, detach=True, remove=True)
    print("  redis started")

# 3. Start postgres with our credentials
print("Starting postgres with eixo:eixo_dev_pass...")
container = c.containers.run('postgres:16', name='eixo-postgres',
    environment={
        'POSTGRES_DB': 'eixo_do_mal',
        'POSTGRES_USER': 'eixo',
        'POSTGRES_PASSWORD': 'eixo_dev_pass'
    },
    ports={'5432/tcp': 5432},
    detach=True,
    remove=True,
)
print(f"  postgres started: {container.id[:12]}")

# 4. Wait for postgres to be ready
print("Waiting for postgres to be healthy...")
for i in range(30):
    container.reload()
    if container.status == 'running':
        logs = container.logs(tail=10).decode()
        if 'database system is ready to accept connections' in logs:
            print(f"  postgres ready after {i+1}s")
            break
    time.sleep(1)
else:
    print("  WARNING: postgres may not be ready yet")
    print("  last logs:", container.logs(tail=5).decode())

print("\nDONE - containers:", [(x.name, x.status) for x in c.containers.list()])
