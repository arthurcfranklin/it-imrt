from fastapi import FastAPI

app = FastAPI(
    title="IT-IMRT API",
    description="API for IT infrastructure monitoring and asset reporting.",
    version="0.1.0-alpha",
)


@app.get("/")
def root():
    return {
        "project": "IT Infrastructure Monitoring & Asset Reporting Tool",
        "status": "running",
        "version": "0.1.0-alpha",
    }