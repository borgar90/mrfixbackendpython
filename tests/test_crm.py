# tests/test_crm.py

import pytest

def create_test_customer(client):
    """
    Hjelpefunksjon: opprett en dummy-kunde og returner ID.
    """
    payload = {
        "first_name": "CRM",
        "last_name": "Kunde",
        "email": "crm.kunde@example.com"
    }
    response = client.post("/customers", json=payload)
    assert response.status_code == 201
    return response.json()["id"]

def test_create_crm_note_and_read(client):
    """
    Test at vi kan opprette et CRM-notat og hente det via GET /crm/notes/{customer_id}
    """
    # Opprett kunde
    customer_id = create_test_customer(client)

    # Opprett CRM-notat
    note_payload = {
        "customer_id": customer_id,
        "note": "Dette er et testnotat for CRM."
    }
    response = client.post("/crm/notes", json=note_payload)
    assert response.status_code == 201
    crm_data = response.json()
    assert crm_data["customer_id"] == customer_id
    assert "id" in crm_data

    # Hent alle notater for kunden
    response_get = client.get(f"/crm/notes/{customer_id}")
    assert response_get.status_code == 200
    notes = response_get.json()
    assert isinstance(notes, list)
    assert len(notes) == 1
    assert notes[0]["note"] == "Dette er et testnotat for CRM."
