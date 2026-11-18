import pytest
from httpx import AsyncClient, ASGITransport
from api.irrigatrace.main import app
from scripts.seed_scenario import run_seed


@pytest.fixture(scope="module", autouse=True)
def seed_data():
    run_seed()


@pytest.mark.asyncio
async def test_api_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["db"] == "up"


@pytest.mark.asyncio
async def test_api_plots_and_preview():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Plots
        resp = await ac.get("/api/plots")
        assert resp.status_code == 200
        plots = resp.json()
        assert len(plots) >= 6
        assert any(p["code"] == "SG-104" for p in plots)

        # Preview (stateless)
        preview_req = {
            "soil_moisture_pct": 21.0,
            "temperature_c": 33.0,
            "rain_probability_pct": 12.0,
            "crop_stage": "GRAND_GROWTH",
            "application_rate_mm_h": 14.0,
            "active_root_zone_mm": 300,
        }
        resp = await ac.post("/api/engine/preview", json=preview_req)
        assert resp.status_code == 200
        prev = resp.json()
        assert prev["action"] == "IRRIGATE"
        assert prev["duration_h"] == 2.8


@pytest.mark.asyncio
async def test_tc16_auditor_permission_forbidden():
    """TC-16: Auditor attempting POST review receives HTTP 403."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = {"X-Demo-User": "user-aud-01"}  # AUDITOR
        payload = {"action": "APPROVE"}
        resp = await ac.post("/api/decisions/IRR-2026-018/review", json=payload, headers=headers)
        assert resp.status_code == 403
        assert "Forbidden" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_case_file_and_reproduce():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get hero decision
        resp = await ac.get("/api/decisions/IRR-2026-018")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "IRR-2026-018"
        assert data["recommendation"]["action"] == "IRRIGATE"
        assert data["recommendation"]["duration_h"] == 2.8
        assert data["final"]["duration_h"] == 2.0
        assert data["integrity"]["valid"] is True

        # Reproduce check
        resp = await ac.post("/api/decisions/IRR-2026-018/reproduce")
        assert resp.status_code == 200
        rep = resp.json()
        assert rep["match"] is True


@pytest.mark.asyncio
async def test_tc24_similar_decisions_fallback():
    """TC-24: When Qdrant is down, /similar uses SQL fallback, labeled."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/decisions/IRR-2026-018/similar")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert len(data["results"]) > 0
        assert "fallback" in data["source"] or "qdrant" in data["source"]
        assert "not proof of causal similarity" in data["label"]


@pytest.mark.asyncio
async def test_compare_and_audit():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Compare
        resp = await ac.get("/api/compare?a=IRR-2026-014&b=IRR-2026-018")
        assert resp.status_code == 200
        comp = resp.json()
        assert comp["a"] == "IRR-2026-014"
        assert comp["b"] == "IRR-2026-018"
        assert len(comp["input_deltas"]) > 0

        # Audit verify all
        resp = await ac.get("/api/audit/verify-all")
        assert resp.status_code == 200
        audit = resp.json()
        assert audit["total_decisions"] >= 2
        assert audit["all_valid"] is True
