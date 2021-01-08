import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from odmantic.engine import AIOEngine
from odmantic.fastapi import AIOEngineDependency
from odmantic.model import Model
from tests.integration.conftest import TEST_MONGO_MODE, MongoMode

pytestmark = pytest.mark.skipif(
    TEST_MONGO_MODE != MongoMode.DEFAULT,
    reason="Only test dependency with the default Mongo instance "
    "running on localhost:27017",
)


@pytest.mark.asyncio
async def test_fastapi_dependency_return_value():
    my_dep = AIOEngineDependency()
    engine = await my_dep()
    assert isinstance(engine, AIOEngine)


@pytest.mark.asyncio
async def test_fastapi_dependency_custom_database_name():
    my_dep = AIOEngineDependency(database="mydb")
    engine = await my_dep()
    assert engine.database_name == "mydb"


@pytest.mark.asyncio
async def test_fastapi_dependency_cache_logic():
    my_dep = AIOEngineDependency()
    engine1 = await my_dep()
    engine2 = await my_dep()
    assert engine1 is engine2


def test_fastapi_dependency_with_fastapi(fastapi_app: FastAPI, test_client: TestClient):
    EngineD = AIOEngineDependency()

    @fastapi_app.get("/")
    async def get(engine: AIOEngine = EngineD):
        assert isinstance(engine, AIOEngine)

        class M(Model):
            ...

        await engine.find(M)

    response = test_client.get("/")
    assert response.status_code == 200


def test_fastapi_dependency_custom_uri(fastapi_app: FastAPI, test_client: TestClient):
    EngineD = AIOEngineDependency("mongodb://localhost:27017/")

    @fastapi_app.get("/")
    async def get(engine: AIOEngine = EngineD):
        assert isinstance(engine, AIOEngine)

        class M(Model):
            ...

        await engine.find(M)

    response = test_client.get("/")
    assert response.status_code == 200


def test_fastapi_dependency_deprecation_warning():
    with pytest.warns(
        DeprecationWarning, match="the AIOEngineDependency object is deprecated"
    ):
        AIOEngineDependency()
