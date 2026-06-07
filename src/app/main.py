from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from fastapi.staticfiles import StaticFiles

from src.app.api.assets import router as assets_router
from src.app.database.db import Base, SessionLocal, engine
from src.app.models.asset import Asset

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IT-IMRT API",
    description="API for IT infrastructure monitoring and asset reporting.",
    version="0.1.0-alpha",
)

app.mount(
    "/static",
    StaticFiles(directory="src/app/static"),
    name="static"
)

templates = Jinja2Templates(directory="src/app/templates")

app.include_router(assets_router)


@app.get("/")
def root():
    return {
        "project": "IT Infrastructure Monitoring & Asset Reporting Tool",
        "status": "running",
        "version": "0.1.0-alpha",
    }


@app.get("/dashboard")
def dashboard(
    request: Request,
    search: str | None = Query(default=None),
    error: str | None = Query(default=None),
    success: str | None = Query(default=None),
):
    db = SessionLocal()

    query = db.query(Asset)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Asset.hostname.ilike(search_filter))
            | (Asset.ip_address.ilike(search_filter))
            | (Asset.operating_system.ilike(search_filter))
            | (Asset.asset_type.ilike(search_filter))
            | (Asset.status.ilike(search_filter))
        )

    assets = query.order_by(Asset.id.desc()).all()
    all_assets = db.query(Asset).all()

    total_assets = len(all_assets)
    online_assets = len([asset for asset in all_assets if asset.status.lower() == "online"])
    offline_assets = len([asset for asset in all_assets if asset.status.lower() == "offline"])

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "assets": assets,
            "total_assets": total_assets,
            "online_assets": online_assets,
            "offline_assets": offline_assets,
            "search": search or "",
            "error": error,
            "success": success,
        },
    )


@app.post("/dashboard/assets/create")
def create_asset_web(
    hostname: str = Form(...),
    ip_address: str = Form(...),
    url: str | None = Form(default=None),
    operating_system: str = Form(...),
    asset_type: str = Form(...),
    status: str = Form(...),
):
    db = SessionLocal()

    new_asset = Asset(
        hostname=hostname,
        ip_address=ip_address,
        url=url,
        operating_system=operating_system,
        asset_type=asset_type,
        status=status,
    )

    try:
        db.add(new_asset)
        db.commit()
    except IntegrityError:
        db.rollback()
        db.close()
        return RedirectResponse(
            url="/dashboard?error=Hostname ou endereço IP já cadastrado em outro ativo.",
            status_code=303,
        )

    db.close()

    return RedirectResponse(
        url="/dashboard?success=Ativo cadastrado com sucesso.",
        status_code=303,
    )


@app.post("/dashboard/assets/update/{asset_id}")
def update_asset_web(
    asset_id: int,
    hostname: str = Form(...),
    ip_address: str = Form(...),
    url: str | None = Form(default=None),
    operating_system: str = Form(...),
    asset_type: str = Form(...),
    status: str = Form(...),
):
    db = SessionLocal()

    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        db.close()
        raise HTTPException(status_code=404, detail="Asset not found")

    asset.hostname = hostname
    asset.ip_address = ip_address
    asset.operating_system = operating_system
    asset.asset_type = asset_type
    asset.status = status
    asset.url = url

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        db.close()
        return RedirectResponse(
            url="/dashboard?error=Hostname ou endereço IP já cadastrado em outro ativo.",
            status_code=303,
        )

    db.close()

    return RedirectResponse(
        url="/dashboard?success=Ativo atualizado com sucesso.",
        status_code=303,
    )


@app.post("/dashboard/assets/delete/{asset_id}")
def delete_asset_web(asset_id: int):
    db = SessionLocal()

    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset:
        db.delete(asset)
        db.commit()

    db.close()

    return RedirectResponse(
        url="/dashboard?success=Ativo excluído com sucesso.",
        status_code=303,
    )