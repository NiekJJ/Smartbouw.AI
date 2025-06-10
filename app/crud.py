from sqlalchemy.orm import Session
from sqlalchemy import or_, asc
from . import models, schemas
from datetime import date

# ======================
# KLANT CRUD
# ======================

def create_klant(db: Session, klant: schemas.KlantCreate):
    klant_data = klant.dict()
    if not klant_data.get("registratiedatum"):
        klant_data["registratiedatum"] = date.today()
    db_klant = models.Klant(**klant_data)
    db.add(db_klant)
    db.commit()
    db.refresh(db_klant)
    return db_klant

def get_klanten(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Klant).offset(skip).limit(limit).all()

def get_klant(db: Session, klant_id: int):
    return db.query(models.Klant).filter(models.Klant.id == klant_id).first()

def zoek_klanten(db: Session, zoekterm: str):
    zoekterm = f"%{zoekterm.lower()}%"
    return (
        db.query(models.Klant)
        .filter(
            or_(
                models.Klant.voornaam.ilike(zoekterm),
                models.Klant.achternaam.ilike(zoekterm),
                models.Klant.straatnaam.ilike(zoekterm),
                models.Klant.huisnummer.ilike(zoekterm),
                models.Klant.woonplaats.ilike(zoekterm),
                models.Klant.postcode.ilike(zoekterm),
                models.Klant.email.ilike(zoekterm),
                models.Klant.telefoon.ilike(zoekterm),
                models.Klant.klantnummer.ilike(zoekterm),
                models.Klant.klanttype.ilike(zoekterm),
            )
        )
        .order_by(asc(models.Klant.achternaam))
        .all()
    )

def is_email_in_use(db: Session, email: str, exclude_klant_id: int | None = None) -> bool:
    query = db.query(models.Klant).filter(models.Klant.email == email)
    if exclude_klant_id:
        query = query.filter(models.Klant.id != exclude_klant_id)
    return db.query(query.exists()).scalar()

def is_klantnummer_in_use(db: Session, klantnummer: str, exclude_klant_id: int | None = None) -> bool:
    query = db.query(models.Klant).filter(models.Klant.klantnummer == klantnummer)
    if exclude_klant_id:
        query = query.filter(models.Klant.id != exclude_klant_id)
    return db.query(query.exists()).scalar()

def update_klant(db: Session, klant_id: int, klant: schemas.KlantCreate):
    db_klant = db.query(models.Klant).filter(models.Klant.id == klant_id).first()
    if not db_klant:
        return None
    for key, value in klant.dict().items():
        setattr(db_klant, key, value)
    db.commit()
    db.refresh(db_klant)
    return db_klant

def delete_klant(db: Session, klant_id: int):
    db_klant = db.query(models.Klant).filter(models.Klant.id == klant_id).first()
    if db_klant:
        db.delete(db_klant)
        db.commit()

# ======================
# PROJECT CRUD
# ======================

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        projectnaam=project.projectnaam,
        klant_id=project.klant_id,
        omschrijving=project.omschrijving,
        straat=project.straat,
        postcode=project.postcode,
        woonplaats=project.woonplaats,
        status=project.status,
        startdatum=project.startdatum,
        einddatum=project.einddatum,
        installateurs=project.installateurs
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    for taak in project.taken:
        db_taak = models.Taak(**taak.dict(), project_id=db_project.id)
        db.add(db_taak)

    for afspraak in project.afspraken:
        db_afspraak = models.Afspraak(**afspraak.dict(), project_id=db_project.id)
        db.add(db_afspraak)

    for doc in project.documenten:
        db_doc = models.Document(**doc.dict(), project_id=db_project.id)
        db.add(db_doc)

    db.commit()
    return db_project

def get_projecten(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).order_by(models.Project.startdatum).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def update_project_status(db: Session, project_id: int, status: str):
    project = get_project(db, project_id)
    if project:
        project.status = status
        db.commit()
        db.refresh(project)
    return project

def update_installateurs(db: Session, project_id: int, installateurs: str):
    project = get_project(db, project_id)
    if project:
        project.installateurs = installateurs
        db.commit()
        db.refresh(project)
    return project

def add_taak_to_project(db: Session, project_id: int, taak: schemas.TaakCreate):
    db_taak = models.Taak(**taak.dict(), project_id=project_id)
    db.add(db_taak)
    db.commit()
    db.refresh(db_taak)
    return db_taak

def update_taak_status(db: Session, taak_id: int, status: str):
    taak = db.query(models.Taak).filter(models.Taak.id == taak_id).first()
    if taak:
        taak.status = status
        db.commit()
        db.refresh(taak)
    return taak

def delete_taak(db: Session, taak_id: int):
    taak = db.query(models.Taak).filter(models.Taak.id == taak_id).first()
    if taak:
        db.delete(taak)
        db.commit()

from .models import DocumentMap, Document

def create_document_map(db: Session, project_id: int, map_data: schemas.DocumentMapCreate):
    db_map = DocumentMap(naam=map_data.naam, project_id=project_id)
    db.add(db_map)
    db.commit()
    db.refresh(db_map)
    return db_map

def get_document_mappen(db: Session, project_id: int):
    return db.query(DocumentMap).filter(DocumentMap.project_id == project_id).all()

def upload_document(db: Session, document: schemas.DocumentCreate):
    db_doc = Document(
        bestandsnaam=document.bestandsnaam,
        pad=document.pad,
        map_id=document.map_id,
        project_id=document.project_id,
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_documenten_in_map(db: Session, map_id: int):
    return db.query(Document).filter(Document.map_id == map_id).all()

def delete_document(db: Session, document_id: int):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc:
        db.delete(doc)
        db.commit()
    return doc