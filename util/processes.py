import os
from rdflib import Graph
import importlib.resources
from .process_pipeline_builder import ProcessPipelineBuilder




def get_processes(mmut_path: str) -> ProcessPipelineBuilder:

    # RDF-Graph erzeugen
    g = Graph()

    # Datei im Turtle-Format einlesen
    with importlib.resources.files('py_mmut_rdf').joinpath('mmut.ttl').open('r', encoding='UTF-8') as f:
        ttl_data = f.read()
        print("Parsing Turtle data...")
        g.parse(data=ttl_data, format="turtle")

    for file in os.listdir(mmut_path):

        if file.endswith('.ttl'):
            print(f"Parsing Turtle file: {file}")
            ttl_file = os.path.join(mmut_path, file)
            g.parse(ttl_file, format="turtle")

    return ProcessPipelineBuilder(g)
