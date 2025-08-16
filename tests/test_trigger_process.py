import pytest
import os
from unittest.mock import patch
from util.trigger_process import is_valid_uuid, trigger_process
from util.process_pipeline_builder import ProcessPipelineBuilder

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



def test_trigger_process_value_uuid(data_dir):

    with patch("util.trigger_process.get_mmut_dir", return_value=data_dir / "mmut"):
        with patch("util.trigger_process.run_docker_flow_sync", return_value=None) as mock_run:
            trigger_process("833eee11-12f7-400d-ada8-0733c37a5563")
            mock_run.assert_called_once()
            args, _ = mock_run.call_args
            # Ensure the first argument is a ProcessPipelineBuilder instance
            assert len(args) == 1
            assert isinstance(args[0], ProcessPipelineBuilder)