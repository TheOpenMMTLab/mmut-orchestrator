import os
from rdflib import Graph
import importlib.resources
from .process_pipeline_builder import ProcessPipelineBuilder
from .helper import get_mmut_dir


def get_processes(mmut_id: str):

    # RDF-Graph erzeugen
    g = Graph()

    # Datei im Turtle-Format einlesen
    with importlib.resources.files('py_mmut_rdf').joinpath('mmut.ttl').open('r', encoding='UTF-8') as f:
        ttl_data = f.read()
        print("Parsing Turtle data...")
        g.parse(data=ttl_data, format="turtle")

    for file in os.listdir(os.path.join(get_mmut_dir(), mmut_id)):
        print(f"Parsing Turtle file: {file}")

        if file.endswith('.ttl'):
            ttl_file = os.path.join(get_mmut_dir(), mmut_id, file)
            g.parse(ttl_file, format="turtle")


    return ProcessPipelineBuilder(g)
