from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from . import models, schemas, crud
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================
# KLANT ROUTES
# ======================

@app.post("/klanten/", response_model=schemas.KlantOut)
def create_klant(klant: schemas.KlantCreate, db: Session = Depends(get_db)):
    return crud.create_klant(db, klant)

@app.get("/klanten/", response_model=List[schemas.KlantOut])
def get_klanten(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_klanten(db, skip=skip, limit=limit)

@app.get("/klanten/zoek/", response_model=List[schemas.KlantOut])
def zoek_klanten(zoekterm: str, db: Session = Depends(get_db)):
    return crud.zoek_klanten(db, zoekterm)

@app.get("/klanten/{klant_id}", response_model=schemas.KlantOut)
def get_klant(klant_id: int, db: Session = Depends(get_db)):
    klant = crud.get_klant(db, klant_id)
    if klant is None:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")
    return klant

@app.put("/klanten/{klant_id}", response_model=schemas.KlantOut)
def update_klant(klant_id: int, klant: schemas.KlantCreate, db: Session = Depends(get_db)):
    updated_klant = crud.update_klant(db, klant_id, klant)
    if updated_klant is None:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")
    return updated_klant

@app.delete("/klanten/{klant_id}")
def delete_klant(klant_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_klant(db, klant_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")
    return {"message": "Klant verwijderd"}

# ======================
# PROJECT ROUTES
# ======================

@app.post("/projecten/", response_model=schemas.ProjectOut)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project)

@app.get("/projecten/", response_model=List[schemas.ProjectOut])
def get_projecten(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_projecten(db, skip=skip, limit=limit)

@app.get("/projecten/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project niet gevonden")
    return project

@app.put("/projecten/{project_id}/status")
def update_project_status(project_id: int, status: str, db: Session = Depends(get_db)):
    project = crud.update_project_status(db, project_id, status)
    if project is None:
        raise HTTPException(status_code=404, detail="Project niet gevonden")
    return {"message": "Status bijgewerkt", "status": status}

# ======================
# TAAK ROUTES
# ======================

@app.post("/projecten/{project_id}/taken", response_model=schemas.TaakOut)
def add_taak(project_id: int, taak: schemas.TaakCreate, db: Session = Depends(get_db)):
    return crud.add_taak_to_project(db, project_id, taak)

@app.put("/taken/{taak_id}/status", response_model=schemas.TaakOut)
def update_taak_status(taak_id: int, status: str, db: Session = Depends(get_db)):
    taak = crud.update_taak_status(db, taak_id, status)
    if taak is None:
        raise HTTPException(status_code=404, detail="Taak niet gevonden")
    return taak

# ======================
# DOCUMENTMAPPEN ROUTES
# ======================

@app.post("/projecten/{project_id}/mappen", response_model=schemas.DocumentMapOut)
def create_map(project_id: int, map_data: schemas.DocumentMapCreate, db: Session = Depends(get_db)):
    return crud.create_document_map(db, project_id, map_data)

@app.get("/projecten/{project_id}/mappen", response_model=List[schemas.DocumentMapOut])
def get_mappen(project_id: int, db: Session = Depends(get_db)):
    return crud.get_document_mappen(db, project_id)

@app.put("/mappen/{map_id}", response_model=schemas.DocumentMapOut)
def update_map(map_id: int, map_data: schemas.DocumentMapCreate, db: Session = Depends(get_db)):
    updated = crud.update_document_map(db, map_id, map_data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Map niet gevonden")
    return updated

@app.delete("/mappen/{map_id}")
def delete_map(map_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_document_map(db, map_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Map niet gevonden")
    return {"message": "Map verwijderd"}

# ======================
# DOCUMENT UPLOAD/DOWNLOAD ROUTES
# ======================

UPLOAD_DIR = "uploads/projecten"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/documenten/upload/")
def upload_document(
    project_id: int = Form(...),
    map_id: Optional[int] = Form(None),
    file: UploadFile = File(...)
):
    filename = file.filename
    project_folder = os.path.join(UPLOAD_DIR, f"project_{project_id}")
    os.makedirs(project_folder, exist_ok=True)

    filepath = os.path.join(project_folder, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())

    document_create = schemas.DocumentCreate(
        bestandsnaam=filename,
        pad=filepath,
        map_id=map_id,
        project_id=project_id
    )
    db = SessionLocal()
    try:
        crud.upload_document(db, document_create)
    finally:
        db.close()

    return {
        "message": "Bestand succesvol geüpload",
        "bestandsnaam": filename,
        "map_id": map_id,
        "pad": filepath
    }

@app.get("/documenten/download/{project_id}/{bestandsnaam}")
def download_document(project_id: int, bestandsnaam: str):
    filepath = os.path.join(UPLOAD_DIR, f"project_{project_id}", bestandsnaam)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Bestand niet gevonden")
    return FileResponse(filepath, filename=bestandsnaam)
