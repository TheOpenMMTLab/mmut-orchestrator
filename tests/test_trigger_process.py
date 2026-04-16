import pytest
import os
from typing import List
from unittest.mock import patch
from util.trigger_process import is_valid_uuid, trigger_process
from util.process_pipeline_builder import Process

def test_is_valid_uuid():
    """Test the is_valid_uuid function"""
    assert is_valid_uuid("44f138a6-5c58-4b62-8770-ac5f4739ac44")
    assert not is_valid_uuid("invalid-uuid")


def test_trigger_process_invalid_uuid():
    """Test the trigger_process function"""
    with pytest.raises(ValueError):
        trigger_process("invalid-uuid")


def test_trigger_process_random_uuid():
    """Test the trigger_process function"""
    with pytest.raises(ValueError):
        trigger_process("44f138a6-5c58-4b62-8770-ac5f4739ac44")


def test_trigger_process_valid(data_dir):

    with patch("util.trigger_process.get_mmut_dir", return_value=data_dir / "mmut"):
        with patch("util.trigger_process.run_docker_flow_sync", return_value=None) as mock_run:
            trigger_process("833eee11-12f7-400d-ada8-0733c37a5563")
            mock_run.assert_called_once()
            args, _ = mock_run.call_args
            # Ensure call signature is (processes, flow_name)
            assert len(args) == 2
            assert len(args[0]) == 3
            assert args[1] == "mmut-833eee11-12f7-400d-ada8-0733c37a5563"
            # Test EVA (Eingabe, Verarbeitung, Ausgabe)
            assert args[0][0].id ==  "http://hpi.de/test-valid#SysMLMicroModel-SysML"
            assert args[0][1].id ==  "http://hpi.de/test-valid#PythonScriptTransformation-a"
            assert args[0][2].id ==  "http://hpi.de/test-valid#RDFMicroModel-rdf"

def test_trigger_process_valid_complex(data_dir):

    with patch("util.trigger_process.get_mmut_dir", return_value=data_dir / "mmut"):
        with patch("util.trigger_process.run_docker_flow_sync", return_value=None) as mock_run:
            trigger_process("8014cf0a-8d29-4cdb-9563-6b0e9fcf4b8f")
            mock_run.assert_called_once()
            args, _ = mock_run.call_args
            # Ensure call signature is (processes, flow_name)
            assert len(args) == 2
            assert len(args[0]) == 7
            assert args[1] == "mmut-8014cf0a-8d29-4cdb-9563-6b0e9fcf4b8f"
            # Test EVA (Eingabe, Verarbeitung, Ausgabe)
            assert args[0][0].id ==  "http://hpi.de/test-valid-complex#SysMLMicroModel-Model-A2"
            assert args[0][1].id ==  "http://hpi.de/test-valid-complex#SysMLMicroModel-Model-A3"
            assert args[0][2].id ==  "http://hpi.de/test-valid-complex#PythonScriptTransformation-a"
            assert args[0][3].id ==  "http://hpi.de/test-valid-complex#PythonScriptTransformation-c"
            assert args[0][4].id ==  "http://hpi.de/test-valid-complex#RDFMicroModel-Model-A1"
            assert args[0][5].id ==  "http://hpi.de/test-valid-complex#PythonScriptTransformation-b"
            assert args[0][6].id ==  "http://hpi.de/test-valid-complex#RDFMicroModel-Output-Model"


def test_trigger_process_no_process(data_dir):

    with patch("util.trigger_process.get_mmut_dir", return_value=data_dir / "mmut"):
        with patch("util.trigger_process.run_docker_flow_sync", return_value=None) as mock_run:
            with pytest.raises(ValueError):
                trigger_process("fed76341-fc1e-4669-b221-1d16156c7d53")
            mock_run.assert_not_called()

def test_trigger_process_loop(data_dir):

    with patch("util.trigger_process.get_mmut_dir", return_value=data_dir / "mmut"):
        with patch("util.trigger_process.run_docker_flow_sync", return_value=None) as mock_run:
            with pytest.raises(ValueError):
                trigger_process("25350c66-f832-4c8d-b1cf-5b49e890806d")
            mock_run.assert_not_called()
          
            