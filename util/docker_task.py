import time
from docker import DockerClient
from prefect import task, get_run_logger
from prefect.states import Failed


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
