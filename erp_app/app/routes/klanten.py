from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import get_db
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/klanten",
    tags=["klanten"]
)

@router.post("/", response_model=schemas.KlantOut)
def create_klant(klant: schemas.KlantCreate, db: Session = Depends(get_db)):
    if crud.is_email_in_use(db, klant.email):
        raise HTTPException(status_code=400, detail="E-mail is al in gebruik")
    if crud.is_klantnummer_in_use(db, klant.klantnummer):
        raise HTTPException(status_code=400, detail="Klantnummer is al in gebruik")
    return crud.create_klant(db=db, klant=klant)


@router.put("/{klant_id}")
def update_klant(klant_id: int, klant_data: schemas.KlantCreate, db: Session = Depends(get_db)):
    bestaand_klant = crud.get_klant(db, klant_id=klant_id)
    if not bestaand_klant:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")

    if crud.is_email_in_use(db, klant_data.email, exclude_klant_id=klant_id):
        raise HTTPException(status_code=400, detail="E-mail is al in gebruik door een andere klant")
    if crud.is_klantnummer_in_use(db, klant_data.klantnummer, exclude_klant_id=klant_id):
        raise HTTPException(status_code=400, detail="Klantnummer is al in gebruik door een andere klant")

    bijgewerkt_klant = crud.update_klant(db, klant_id=klant_id, klant=klant_data)
    return JSONResponse(
        status_code=200,
        content={
            "message": "Klant succesvol bijgewerkt",
            "klant": schemas.KlantOut.model_validate(bijgewerkt_klant).model_dump()
        }
    )

@router.get("/zoek", response_model=list[schemas.KlantOut])
def zoek_klanten(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    resultaten = crud.zoek_klanten(db, zoekterm=query)
    if not resultaten:
        raise HTTPException(status_code=404, detail=f"Geen klanten gevonden voor zoekterm: '{query}'")
    return resultaten

@router.get("/", response_model=list[schemas.KlantOut])
def list_klanten(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_klanten(db, skip=skip, limit=limit)

@router.get("/{klant_id}", response_model=schemas.KlantOut)
def read_klant(klant_id: int, db: Session = Depends(get_db)):
    db_klant = crud.get_klant(db, klant_id=klant_id)
    if db_klant is None:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")
    return db_klant

@router.delete("/{klant_id}")
def delete_klant(klant_id: int, db: Session = Depends(get_db)):
    bestaand_klant = crud.get_klant(db, klant_id=klant_id)
    if not bestaand_klant:
        raise HTTPException(status_code=404, detail="Klant niet gevonden")

    crud.delete_klant(db, klant_id=klant_id)
    return JSONResponse(
        status_code=200,
        content={"message": f"Klant met ID {klant_id} succesvol verwijderd"}
    )