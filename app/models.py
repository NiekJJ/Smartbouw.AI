from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, date
import enum


# =====================
# ENUMS
# =====================

class KlantTypeEnum(str, enum.Enum):
    particulier = "particulier"
    zakelijk = "zakelijk"
    leverancier = "leverancier"

class ProjectStatusEnum(str, enum.Enum):
    ingepland = "ingepland"
    bezig = "bezig"
    afgerond = "afgerond"

class TaakStatusEnum(str, enum.Enum):
    open = "open"
    bezig = "bezig"
    afgerond = "afgerond"

# =====================
# KLANTEN
# =====================

class Klant(Base):
    __tablename__ = "klanten"

    id = Column(Integer, primary_key=True, index=True)
    voornaam = Column(String, index=True)
    achternaam = Column(String, index=True)
    straatnaam = Column(String)
    huisnummer = Column(String)
    postcode = Column(String, index=True)
    woonplaats = Column(String)
    email = Column(String, unique=True, index=True)
    telefoon = Column(String)
    klantnummer = Column(String, unique=True, index=True)
    registratiedatum = Column(Date, default=date.today)
    klanttype = Column(Enum(KlantTypeEnum))


# =====================
# PROJECTEN
# =====================

class Project(Base):
    __tablename__ = "projecten"

    id = Column(Integer, primary_key=True, index=True)
    projectnaam = Column(String, index=True)
    klant_id = Column(Integer, ForeignKey("klanten.id"))
    omschrijving = Column(Text)
    straat = Column(String)
    postcode = Column(String)
    woonplaats = Column(String)
    status = Column(Enum(ProjectStatusEnum), default="ingepland")
    startdatum = Column(Date)
    einddatum = Column(Date)
    installateurs = Column(String)
    aangemaakt_op = Column(DateTime, default=datetime.utcnow)
    bijgewerkt_op = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    klant = relationship("Klant")
    taken = relationship("Taak", back_populates="project", cascade="all, delete-orphan")
    afspraken = relationship("Afspraak", back_populates="project", cascade="all, delete-orphan")
    documenten = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    mappen = relationship("DocumentMap", back_populates="project", cascade="all, delete-orphan")


# =====================
# TAKEN
# =====================

class Taak(Base):
    __tablename__ = "taken"

    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String)
    status = Column(Enum(TaakStatusEnum), default="open")
    uitvoerder = Column(String)
    kleur = Column(String)  # HEX-kleurcode zoals "#FF0000"
    datum = Column(Date)

    project_id = Column(Integer, ForeignKey("projecten.id"))
    project = relationship("Project", back_populates="taken")


# =====================
# AFSPRAKEN
# =====================

class Afspraak(Base):
    __tablename__ = "afspraken"

    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String)
    datum = Column(Date)
    notities = Column(Text)

    project_id = Column(Integer, ForeignKey("projecten.id"))
    project = relationship("Project", back_populates="afspraken")


# =====================
# DOCUMENTEN
# =====================

class DocumentMap(Base):
    __tablename__ = "documentmappen"

    id = Column(Integer, primary_key=True, index=True)
    naam = Column(String)

    project_id = Column(Integer, ForeignKey("projecten.id"))
    project = relationship("Project", back_populates="mappen")
    documenten = relationship("Document", back_populates="map", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documenten"

    id = Column(Integer, primary_key=True, index=True)
    bestandsnaam = Column(String)
    pad = Column(String)

    project_id = Column(Integer, ForeignKey("projecten.id"))
    map_id = Column(Integer, ForeignKey("documentmappen.id"))

    project = relationship("Project", back_populates="documenten")
    map = relationship("DocumentMap", back_populates="documenten")
