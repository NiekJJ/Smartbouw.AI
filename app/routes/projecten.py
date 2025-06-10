from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/projecten",
    tags=["projecten"]
)

@router.get("/", response_model=List[schemas.ProjectOut])
def list_projecten(db: Session = Depends(get_db)):
    return crud.get_projecten(db)

@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project niet gevonden")
    return project

@router.put("/{project_id}/status")
def update_project_status(project_id: int, status: dict, db: Session = Depends(get_db)):
    updated = crud.update_project_status(db, project_id, status["status"])
    if not updated:
        raise HTTPException(status_code=404, detail="Project niet gevonden")
    return {"message": "Status bijgewerkt"}

@router.put("/{project_id}/installateurs")
def update_installateurs(project_id: int, data: dict, db: Session = Depends(get_db)):
    updated = crud.update_installateurs(db, project_id, data["installateurs"])
    if not updated:
        raise HTTPException(status_code=404, detail="Project niet gevonden")
    return {"message": "Installateurs bijgewerkt"}

@router.post("/{project_id}/taken", response_model=schemas.TaakOut)
def voeg_taak_toe(project_id: int, taak: schemas.TaakCreate, db: Session = Depends(get_db)):
    return crud.add_taak_to_project(db, project_id, taak)

@router.delete("/taken/{taak_id}")
def verwijder_taak(taak_id: int, db: Session = Depends(get_db)):
    crud.delete_taak(db, taak_id)
    return {"message": f"Taak {taak_id} verwijderd"}

@router.put("/taken/{taak_id}/status")
def toggle_taak_status(taak_id: int, data: dict, db: Session = Depends(get_db)):
    updated = crud.update_taak_status(db, taak_id, data["status"])
    if not updated:
        raise HTTPException(status_code=404, detail="Taak niet gevonden")
    return {"message": "Taakstatus bijgewerkt"}

@router.post("/documenten/upload/")
def upload_document(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    mapnaam: str = Form(...),
):
    upload_pad = f"uploads/project_{project_id}/{mapnaam}"
    os.makedirs(upload_pad, exist_ok=True)
    bestandspad = os.path.join(upload_pad, file.filename)

    with open(bestandspad, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": f"{file.filename} geüpload"}

@router.delete("/documenten/{document_id}")
def delete_document(document_id: int):
    # Placeholder – later uit te breiden met database koppeling
    return {"message": f"Document {document_id} verwijderd (placeholder)"}
