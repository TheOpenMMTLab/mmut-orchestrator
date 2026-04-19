#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import Set, Tuple

import networkx as nx
from rdflib import Graph, Namespace, RDF


def _ensure_project_root_on_path():
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


MMUT = Namespace("http://frittenburger.de/ontology/mmut#")


def load_ttl_file(uuid: str) -> Graph:
    """Load TTL file for given UUID."""
    project_root = Path(__file__).resolve().parent.parent
    ttl_path = project_root / "mmut" / uuid
    
    # Find the .ttl file in the UUID directory
    ttl_files = list(ttl_path.glob("*.ttl"))
    if not ttl_files:
        raise FileNotFoundError(f"No TTL file found in {ttl_path}")
    
    ttl_file = ttl_files[0]
    g = Graph()
    g.parse(ttl_file, format="turtle")
    return g


def count_transformations(g: Graph) -> int:
    """Count number of transformation nodes."""
    query = f"""
    PREFIX MMUT: <{MMUT}>
    SELECT (COUNT(?t) as ?count)
    WHERE {{
        ?t a MMUT:PythonScriptTransformation .
    }}
    """
    results = g.query(query)
    for row in results:
        return int(row[0])
    return 0


def count_models(g: Graph) -> int:
    """Count number of micro model nodes (by checking rdf:type ends with MicroModel)."""
    count = 0
    RDF_TYPE = RDF.type
    
    for subj, _, _ in g.triples((None, RDF_TYPE, None)):
        # Check if object URI contains "MicroModel"
        for _, _, obj in g.triples((subj, RDF_TYPE, None)):
            if "MicroModel" in str(obj):
                count += 1
                break
    return count


def count_task_definitions(g: Graph) -> int:
    """Count number of task definitions."""
    query = f"""
    PREFIX MMUT: <{MMUT}>
    SELECT (COUNT(?td) as ?count)
    WHERE {{
        ?td a MMUT:TaskDefinition .
    }}
    """
    results = g.query(query)
    for row in results:
        return int(row[0])
    return 0


def build_property_graph(g: Graph) -> Tuple[nx.DiGraph, Set[str], Set[str]]:
    """Build a property graph for longest path analysis."""
    pg = nx.DiGraph()
    input_models: Set[str] = set()
    output_models: Set[str] = set()
    RDF_TYPE = RDF.type

    # Add model nodes: all subjects whose rdf:type contains "MicroModel"
    for subj, _, obj in g.triples((None, RDF_TYPE, None)):
        if "MicroModel" in str(obj):
            model_id = str(subj)
            pg.add_node(model_id, node_type="model")

    # Add transformation nodes
    query = f"""
    PREFIX MMUT: <{MMUT}>
    SELECT ?t
    WHERE {{
        ?t a MMUT:PythonScriptTransformation .
    }}
    """
    results = g.query(query)
    for row in results:
        trans_id = str(row[0])
        pg.add_node(trans_id, node_type="transformation")

    # Add edges: model -> transformation (isInputModelOf)
    query = f"""
    PREFIX MMUT: <{MMUT}>
    SELECT ?m ?t
    WHERE {{
        ?m MMUT:isInputModelOf ?t .
    }}
    """
    results = g.query(query)
    for row in results:
        model_id = str(row[0])
        trans_id = str(row[1])
        pg.add_edge(model_id, trans_id, edge_type="input")

    # Add edges: transformation -> model (hasOutputModel)
    query = f"""
    PREFIX MMUT: <{MMUT}>
    SELECT ?t ?m
    WHERE {{
        ?t MMUT:hasOutputModel ?m .
    }}
    """
    results = g.query(query)
    for row in results:
        trans_id = str(row[0])
        model_id = str(row[1])
        pg.add_edge(trans_id, model_id, edge_type="output")

    # Identify input and output models
    for node in pg.nodes():
        if pg.nodes[node].get("node_type") == "model":
            if pg.in_degree(node) == 0:
                input_models.add(node)
            if pg.out_degree(node) == 0:
                output_models.add(node)

    return pg, input_models, output_models


def count_connected_components(pg: nx.DiGraph) -> int:
    """Count weakly connected components."""
    ug = pg.to_undirected()
    return nx.number_connected_components(ug)


def find_longest_path(pg: nx.DiGraph, inputs: Set[str], outputs: Set[str]) -> int:
    """Find longest path from any input to any output (in terms of transformation count)."""
    if not inputs or not outputs:
        return 0
    
    max_length = 0

    for src in inputs:
        for dst in outputs:
            if src == dst:
                continue
            if not nx.has_path(pg, src, dst):
                continue
            
            try:
                # Find all simple paths and count transformations in longest one
                for path in nx.all_simple_paths(pg, src, dst):
                    trans_count = sum(
                        1 for node in path
                        if pg.nodes[node].get("node_type") == "transformation"
                    )
                    max_length = max(max_length, trans_count)
            except (nx.NetworkXNoPath, nx.NetworkXError):
                pass

    return max_length


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze graph properties of a MMUT process model."
    )
    parser.add_argument("uuid", type=str, help="UUID of the MMUT model")
    args = parser.parse_args()

    try:
        g = load_ttl_file(args.uuid)

        # Calculate metrics
        num_transformations = count_transformations(g)
        num_models = count_models(g)
        num_task_definitions = count_task_definitions(g)

        # Build property graph
        pg, input_models, output_models = build_property_graph(g)

        # Graph analysis
        num_components = count_connected_components(pg)
        longest_path = find_longest_path(pg, input_models, output_models)

        # Output results
        print("Graph Properties")
        print("=" * 50)
        print(f"Number of Transformations:    {num_transformations}")
        print(f"Number of Models:             {num_models}")
        print(f"Number of Task Definitions:   {num_task_definitions}")
        print(f"Connected Components:         {num_components}")
        print(f"Longest Path (Transformations): {longest_path}")
        print("=" * 50)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error analyzing graph: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
