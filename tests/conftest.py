from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def toy_path():
    return FIXTURES / "toy"


@pytest.fixture
def toy(toy_path):
    from boxgraph.store import load_record

    return load_record(toy_path)


@pytest.fixture
def toy_build(toy, tmp_path):
    from boxgraph.engine import Builder

    return Builder(toy, cache_dir=tmp_path / "cache").build()
