import pytest
from django.core import mail
from django.urls import reverse


def test_main_page(client):
    # Open page
    response = client.get(reverse("main"))
    assert response.status_code == 200
    assert b"Hello! And welcome" in response.content


def test_contact_us_page(client, faker):
    # Open page
    response = client.get(reverse("contact_us"))
    assert response.status_code == 200
    assert b"Send us an email!" in response.content

    # Wrong form input: empty email field
    data = {
        "email": "",
        "text": faker.sentence(),
    }
    response = client.post(reverse("contact_us"), data=data)
    assert response.status_code == 200

    # todo: Maybe it's better to check response.context["form"].errors rather than response.content?

    assert b"This field is required" in response.content
    breakpoint()
    assert not mail.outbox

    # Wrong form input: empty text field
    data = {
        "email": faker.email(),
        "text": "",
    }
    response = client.post(reverse("contact_us"), data=data)
    assert response.status_code == 200
    assert b"This field is required" in response.content
    assert not mail.outbox

    # Wrong form input: empty fields
    data = {
        "email": "",
        "text": "",
    }
    response = client.post(reverse("contact_us"), data=data)
    assert response.status_code == 200
    assert response.content.count(b"This field is required") == 2
    assert not mail.outbox

    # Wrong form input: Not an email in the email field
    data = {
        "email": faker.word(),
        "text": faker.sentence(),
    }
    response = client.post(reverse("contact_us"), data=data)
    assert response.status_code == 200
    assert b"Enter a valid email address" in response.content
    assert not mail.outbox

    # Correct form input
    data = {
        "email": faker.email(),
        "text": faker.sentence(),
    }
    response = client.post(reverse("contact_us"), data=data, follow=True)
    assert response.status_code == 200
    assert any(i[0] == reverse("main") for i in response.redirect_chain)
    assert data["email"] in mail.outbox[0].body
    assert data["text"] in mail.outbox[0].body
