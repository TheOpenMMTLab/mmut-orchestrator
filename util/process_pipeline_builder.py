import re
from rdflib import Graph, RDFS
from obse.sparql_queries import SparQLWrapper
from py_mmut_rdf import MMUT
import networkx as nx
import yaml


class Process:
    def __init__(self, id, name, image, command, env, dependencies):
        self.id = id
        self.name = name
        self.image = image
        self.command = command
        self.env = env
        self.dependencies = dependencies


def get_secrets(domain_key, value_key):
    """Retrieve secrets from a secure store."""
    # This is a placeholder function. Replace with actual secret retrieval logic.
    with open("config/secrets.yaml", "r") as f:
        secrets = yaml.safe_load(f)
        return secrets.get(domain_key, {}).get(value_key, None)


def resolve(value):
    """Resolve a value, e.g., by removing prefixes or converting to string."""

    pattern = r"{{resolve:(.*)}}"

    # Nutze eine externe Funktion als Ersatz-Callback
    def ersetze_match(match):
        resolve_instruction = match.group(1).split(":")
        if len(resolve_instruction) == 3 and resolve_instruction[0] == "secrets":
            return get_secrets(resolve_instruction[1], resolve_instruction[2])
        if resolve_instruction[0] == "system":
            if len(resolve_instruction) == 2 and resolve_instruction[1] == "modelpath":
                return "/share/models/"
        raise ValueError(f"Unknown resolve instruction: {match.group(1)}")

    return re.sub(pattern, ersetze_match, value)


class ProcessPipelineBuilder:
    def __init__(self, g: Graph):
        self.sparql_wrapper = SparQLWrapper(g)

        # Graph definieren
        self.G = nx.DiGraph()

        # Knoten (Modell-Prozesse)
        for model in self.sparql_wrapper.get_instances_of_type(MMUT.MicroModel):
            self.G.add_node(model)

        # Knoten (Transformations-Prozesse)
        for transformation in self.sparql_wrapper.get_instances_of_type(MMUT.Transformation):
            self.G.add_node(transformation)

            # Kanten (Abhängigkeiten zwischen Modellen und Transformationen)
            for output_model in self.sparql_wrapper.get_out_references(transformation, MMUT.hasOutputModel):
                self.G.add_edge(transformation, output_model)
            for input_model in self.sparql_wrapper.get_in_references(transformation, MMUT.isInputModelOf):
                self.G.add_edge(input_model, transformation)

    def __iter__(self):
        # Topologische Sortierung der Prozesse (Reihenfolge der Abarbeitung)
        sorted_processes = list(nx.topological_sort(self.G))

        print("Reihenfolge der Prozess-Schritte mit Abhängigkeiten:\n")
        for step in sorted_processes:
            print(f"Prozess {step}.")

            predecessors = list(self.G.predecessors(step))
            dependencies = None
            if predecessors:
                dependencies = [str(pred) for pred in predecessors]

            p_task_definitions = self.sparql_wrapper.get_out_references(step, MMUT.hasTaskDefinition)

            if len(p_task_definitions) == 0:
                print(f"Prozess {step} hat keine Task-Definition.")
                continue

            assert len(p_task_definitions) == 1, f"Prozess {step} hat mehrere Task-Definitionen."
            p_container_property = self.sparql_wrapper.get_single_out_reference(p_task_definitions[0], MMUT.hasContainerProperties)

            image = self.sparql_wrapper.get_single_object_property(p_container_property, MMUT.image)
            p_command_sequence = self.sparql_wrapper.get_single_out_reference(p_container_property, MMUT.hasCommandSequence)
            command = []
            for lit in self.sparql_wrapper.get_sequence(p_command_sequence):
                command.append(resolve(str(lit)))
            p_environment = self.sparql_wrapper.get_single_out_reference(p_container_property, MMUT.hasEnvironment)
            env = {}
            for p_key_value in self.sparql_wrapper.get_out_references(p_environment, MMUT.hasKeyValuePair):
                key = self.sparql_wrapper.get_single_object_property(p_key_value, MMUT.key)
                value = self.sparql_wrapper.get_single_object_property(p_key_value, MMUT.value)
                env[key] = resolve(value)

            yield Process(
                id=str(step),
                name=self.sparql_wrapper.get_single_object_property(p_task_definitions[0], RDFS.label),
                image=image,
                command=command,
                env=env,
                dependencies=dependencies
            )


            
