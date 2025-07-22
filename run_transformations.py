import time
import random
import string
import re
from docker import DockerClient
from prefect import flow, task, get_run_logger
from prefect.states import Failed
from rdflib import Graph
from util.process_pipeline_builder import ProcessPipelineBuilder
import importlib.resources

def to_valid_container_name(name: str) -> str:
    """Convert a name to a valid Docker container name."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '-', name).lower()

@task
def docker_task(params: str):
    logger = get_run_logger()
    logger.info(f"Starte Container {params['name']} ...")

    # Container starten
    client = DockerClient()
    container = client.containers.run(
        image=params['image'],
        name=params['name'],
        detach=True,
        remove=False,
        command=params['command'],
        auto_remove=False,  # Nicht automatisch entfernen, damit wir Logs sehen können
        volumes={
            'D:/Stuff/git/HPI/MicroModelsAndTransformations/orchestrator-poc/models': {
                'bind': '/share/models',
                'mode': 'rw'  # oder 'ro' für read-only
            }
        },
        environment=params['env']
    )

    # Überwachen
    while True:
        container.reload()  # WICHTIG: Status aktualisieren
        status = container.status
        logger.info(f"Container-Status: {status}")

        if status != 'running':
            logger.info("Container ist nicht mehr aktiv.")
            break
        time.sleep(2)

    exit_code = container.attrs['State']['ExitCode']
    logger.info(f"Container beendete sich mit Exit-Code: {exit_code}")


    # Logs ausgeben
    title = ' container logs '
    cnt = 20
    logger.info(cnt * '-' + title + cnt * '-')
    logs = container.logs().decode("utf-8").strip()
    for log in logs.splitlines():
        logger.info(log)
    logger.info((2 * cnt + len(title)) * '=')

    # Container stoppen und entfernen
    logger.info(f"Container {params['name']} wird entfernt.")
    container.remove(force=True)

    if exit_code != 0:
        return Failed(message=f"Container {params['name']} failed with exit code {exit_code}")


@flow(name="mmut")
def docker_flow():
    logger = get_run_logger()
    logger.info("Starte den Flow...")

    # RDF-Graph erzeugen
    g = Graph()

    # Datei im Turtle-Format einlesen
    with importlib.resources.files('py_mmut_rdf').joinpath('mmut.ttl').open('r', encoding='UTF-8') as f:
        ttl_data = f.read()
        print("Parsing Turtle data...")
        g.parse(data=ttl_data, format="turtle")

    g.parse("mmut-squirrl.ttl", format="turtle")

    ppb = ProcessPipelineBuilder(g)

    tasks = {}

    for process in ppb:
        wait_for = []
        if process.dependencies:
            for dep in process.dependencies:
                wait_for.append(tasks[dep])
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=4))

        tasks[process.id] = docker_task.with_options(name=process.name).submit({
            "name": to_valid_container_name(process.name),
            "image": process.image,
            "command": process.command,
            "env": process.env
        }, wait_for=wait_for)

    # Warten, bis alle Tasks fertig sind
    for task_id, task_x in tasks.items():
        logger.info(f"Waiting for task {task_id} to complete...")
        task_x.result()

    logger.info("Flow abgeschlossen.")


if __name__ == "__main__":
    docker_flow()
