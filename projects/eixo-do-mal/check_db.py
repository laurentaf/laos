"""Check if database tables were created."""
import docker

c = docker.from_env()
pg = [x for x in c.containers.list() if 'postgres' in x.name]
if not pg:
    print("No postgres container found")
else:
    container = pg[0]
    exit_code, output = container.exec_run(
        "psql -U shopagent -d shopagent -c 'SELECT table_name FROM information_schema.tables WHERE table_schema = %s' -t",
        environment={"PGPASSWORD": "shopagent"}
    )
    print("Tables in shopagent database:")
    print(output.decode())
