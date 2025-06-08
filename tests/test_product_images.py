# tests/test_product_images.py

import pytest

# Helper to create a product and return its ID

def create_product(client, headers):
    payload = {
        "name": "ImageTestProduct",
        "description": "Product for image tests",
        "price": 49.99,
        "stock": 5
    }
    response = client.post("/products/", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def test_upload_and_list_images(client, admin_headers):
    # Create product
    product_id = create_product(client, admin_headers)
    # Upload image
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    response = client.post(f"/products/{product_id}/images", files=files, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "url" in data
    # URL should be under per-product media folder
    assert data["url"].startswith("/static/") and "/media/" in data["url"]
    assert data.get("is_main") is False
    assert data.get("is_thumbnail") is False
    image_id = data["id"]

    # List images
    resp = client.get(f"/products/{product_id}/images", headers=admin_headers)
    assert resp.status_code == 200
    images = resp.json()
    assert isinstance(images, list)
    assert any(img["id"] == image_id for img in images)

    # Get specific image
    resp2 = client.get(f"/products/{product_id}/images/{image_id}", headers=admin_headers)
    assert resp2.status_code == 200
    img = resp2.json()
    assert img["id"] == image_id


def test_update_image_flags(client, admin_headers):
    # Create product and upload image
    product_id = create_product(client, admin_headers)
    files = {"file": ("test2.png", b"data", "image/png")}
    resp = client.post(f"/products/{product_id}/images", files=files, headers=admin_headers)
    assert resp.status_code == 201
    image_id = resp.json()["id"]
    # Update image flags
    update_payload = {"is_main": True, "is_thumbnail": True}
    r = client.put(f"/products/{product_id}/images/{image_id}", json=update_payload, headers=admin_headers)
    assert r.status_code == 200
    updated = r.json()
    assert updated["is_main"] is True
    assert updated["is_thumbnail"] is True


def test_delete_image(client, admin_headers):
    # Create product and upload image
    product_id = create_product(client, admin_headers)
    files = {"file": ("test3.gif", b"data", "image/gif")}
    resp = client.post(f"/products/{product_id}/images", files=files, headers=admin_headers)
    assert resp.status_code == 201
    image_id = resp.json()["id"]
    # Delete image
    r = client.delete(f"/products/{product_id}/images/{image_id}", headers=admin_headers)
    assert r.status_code == 204
    # Subsequent GET should be 404
    r2 = client.get(f"/products/{product_id}/images/{image_id}", headers=admin_headers)
    assert r2.status_code == 404


def test_upload_image_invalid_product(client, admin_headers):
    # Attempt to upload to non-existent product
    files = {"file": ("test4.png", b"data", "image/png")}
    r = client.post(f"/products/9999/images", files=files, headers=admin_headers)
    assert r.status_code == 404
