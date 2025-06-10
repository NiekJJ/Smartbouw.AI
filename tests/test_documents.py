import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
from io import BytesIO

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models, crud, schemas, main

# Fixture to set up an in-memory SQLite database
@pytest.fixture
def db_session(tmp_path):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper to create a klant and project in the temporary db
@pytest.fixture
def sample_project(db_session):
    klant = models.Klant(
        voornaam="Jan",
        achternaam="Jansen",
        straatnaam="Straat",
        huisnummer="1",
        postcode="1234 AB",
        woonplaats="Plaats",
        email="jan@example.com",
        telefoon="0612345678",
        klantnummer="KLT-0001",
        klanttype="particulier",
    )
    db_session.add(klant)
    db_session.commit()
    db_session.refresh(klant)

    project = models.Project(
        projectnaam="Testproject",
        klant_id=klant.id,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


def test_add_document_to_project(db_session, sample_project):
    doc_path = "/tmp/test.txt"
    document_create = schemas.DocumentCreate(
        bestandsnaam="test.txt",
        pad=doc_path,
        project_id=sample_project.id,
        map_id=None,
    )
    doc = crud.add_document_to_project(db_session, sample_project.id, document_create)
    assert doc.pad == doc_path


def test_upload_document(tmp_path, db_session, sample_project, monkeypatch):
    # Patch SessionLocal used in main.upload_document
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_session.get_bind())
    monkeypatch.setattr(main, "SessionLocal", TestingSessionLocal)

    upload_dir = tmp_path / "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    monkeypatch.setattr(main, "UPLOAD_DIR", str(upload_dir))

    file_content = b"dummy";
    upload_file = main.UploadFile(filename="file.txt", file=BytesIO(file_content))

    main.upload_document(project_id=sample_project.id, map_id=None, file=upload_file)

    # Verify document stored in DB has correct pad
    stored_doc = db_session.query(models.Document).first()
    expected_path = os.path.join(str(upload_dir), f"project_{sample_project.id}", "file.txt")
    assert stored_doc.pad == expected_path
