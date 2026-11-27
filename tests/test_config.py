
import os
import pytest
import importlib
from unittest.mock import patch

from dotenv import load_dotenv


def test_openai_model_is_not_empty():
    with patch("dotenv.load_dotenv"):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "gpt-6-luna"
        }, clear=True):
            from src import config
            importlib.reload(config)

            assert isinstance(config.OPENAI_MODEL, str)
            assert len(config.OPENAI_MODEL.strip()) > 0


def test_openai_api_key_exists():
    with patch("dotenv.load_dotenv"):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key"
        }, clear=True):
            from src import config
            importlib.reload(config)

            assert config.OPENAI_API_KEY is not None
            assert len(config.OPENAI_API_KEY.strip()) > 0


def test_missing_api_key_raises_value_error():
    with patch("dotenv.load_dotenv"):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                importlib.reload(
                    importlib.import_module("src.config")
                )
