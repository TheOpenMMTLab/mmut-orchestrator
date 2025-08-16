from prefect import flow, get_run_logger
from .helper import to_valid_container_name
from .docker_task import docker_task
from .processes import ProcessPipelineBuilder


@flow(name="micro-model-and-transformation")
def docker_flow(pipeline: ProcessPipelineBuilder):
    
    logger = get_run_logger()
    logger.info("Starte den Flow...")

    tasks = {}

    for process in pipeline:
        wait_for = []
        if process.dependencies:
            for dep in process.dependencies:
                if dep not in tasks:
                    raise ValueError(f"Dependency {dep} not found in {tasks.keys()}.")
                wait_for.append(tasks[dep])

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
