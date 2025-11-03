from fastapi import FastAPI
from .routers import telemetry, incidents, priorities, modules, ops

app = FastAPI(title="RBT Prioritization v2 (Incidents + Ops Agent)")

app.include_router(telemetry.router)
app.include_router(incidents.router)
app.include_router(priorities.router)
app.include_router(modules.router)
app.include_router(ops.router)
