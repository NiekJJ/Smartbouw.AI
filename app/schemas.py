from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal, List
from datetime import date, datetime
import re


# =====================
# KLANTEN
# =====================

class KlantBase(BaseModel):
    voornaam: str
    achternaam: str
    straatnaam: str
    huisnummer: str
    postcode: str
    woonplaats: str
    email: EmailStr
    telefoon: str
    klantnummer: str
    klanttype: Literal["particulier", "zakelijk", "leverancier"]

    @validator("telefoon")
    def check_telefoon(cls, v):
        if not re.fullmatch(r"(\+31|0)[1-9][0-9]{8}", v):
            raise ValueError("Ongeldig telefoonnummer. Gebruik bijv. 0612345678 of +31612345678.")
        return v

    @validator("postcode")
    def check_postcode(cls, v):
        if not re.fullmatch(r"\d{4}\s?[A-Z]{2}", v):
            raise ValueError("Postcode moet het Nederlandse formaat hebben, zoals '1234 AB'.")
        return v

    @validator("klantnummer")
    def check_klantnummer(cls, v):
        if not re.fullmatch(r"KLT-\d{4}", v):
            raise ValueError("Klantnummer moet het formaat 'KLT-0001' hebben.")
        return v


class KlantCreate(KlantBase):
    pass


class KlantOut(KlantBase):
    id: int
    registratiedatum: date

    class Config:
        from_attributes = True


# =====================
# TAKEN
# =====================

class TaakBase(BaseModel):
    titel: str
    status: Literal["open", "bezig", "afgerond"] = "open"
    uitvoerder: str
    kleur: Optional[str] = "#000000"
    datum: date


class TaakCreate(TaakBase):
    pass


class TaakUpdate(BaseModel):
    titel: Optional[str] = None
    status: Optional[Literal["open", "bezig", "afgerond"]] = None
    uitvoerder: Optional[str] = None
    kleur: Optional[str] = None
    datum: Optional[date] = None


class TaakOut(TaakBase):
    id: int

    class Config:
        from_attributes = True


# =====================
# AFSPRAKEN
# =====================

class AfspraakBase(BaseModel):
    titel: str
    datum: date
    notities: Optional[str] = None


class AfspraakCreate(AfspraakBase):
    pass


class AfspraakOut(AfspraakBase):
    id: int

    class Config:
        from_attributes = True


# =====================
# DOCUMENTEN
# =====================

class DocumentCreate(BaseModel):
    """Schema for creating a new document."""

    bestandsnaam: str
    pad: str
    project_id: int
    map_id: Optional[int] = None


class DocumentOut(BaseModel):
    id: int
    bestandsnaam: str
    pad: str

    class Config:
        from_attributes = True


class DocumentMapCreate(BaseModel):
    naam: str


class DocumentMapOut(BaseModel):
    id: int
    naam: str
    documenten: List[DocumentOut] = []

    class Config:
        from_attributes = True


# =====================
# PROJECTEN
# =====================

class ProjectBase(BaseModel):
    projectnaam: str
    klant_id: int
    omschrijving: Optional[str] = None
    straat: Optional[str] = None
    postcode: Optional[str] = None
    woonplaats: Optional[str] = None
    status: Literal["ingepland", "bezig", "afgerond"] = "ingepland"
    startdatum: Optional[date] = None
    einddatum: Optional[date] = None
    installateurs: Optional[str] = None


class ProjectCreate(ProjectBase):
    taken: List[TaakCreate] = []
    afspraken: List[AfspraakCreate] = []
    documenten: List[DocumentOut] = []


class ProjectOut(ProjectBase):
    id: int
    klant: KlantOut
    taken: List[TaakOut] = []
    afspraken: List[AfspraakOut] = []
    documenten: List[DocumentOut] = []
    mappen: List[DocumentMapOut] = []
    aangemaakt_op: datetime
    bijgewerkt_op: datetime

    class Config:
        from_attributes = True
