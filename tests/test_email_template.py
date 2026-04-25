# tests/test_email_template.py
from email_template import render_html

def test_render_html_contains_body_text():
    html = render_html(
        body_text="Hola María, te escribimos desde Valoria.",
        cta_text="Descubrir Ahora",
        cta_url="https://valoria.com/eco-trek",
        segmento="VIP",
        img_b64=None,
    )
    assert "Hola María" in html
    assert "Descubrir Ahora" in html
    assert "https://valoria.com/eco-trek" in html

def test_render_html_is_valid_html():
    html = render_html(
        body_text="Texto de prueba.",
        cta_text="Ver Producto",
        cta_url="https://valoria.com",
        segmento="Gen-Z",
        img_b64=None,
    )
    assert html.startswith("<!DOCTYPE html>")
    assert "</html>" in html

def test_render_html_includes_valoria_branding():
    html = render_html(
        body_text="Mensaje.",
        cta_text="CTA",
        cta_url="https://valoria.com",
        segmento="Familias",
        img_b64=None,
    )
    assert "VALORIA" in html
    assert "Sostenible por diseño" in html

def test_render_html_embeds_image_when_provided():
    fake_b64 = "iVBORw0KGgoAAAANS"
    html = render_html(
        body_text="Mensaje.",
        cta_text="CTA",
        cta_url="https://valoria.com",
        segmento="VIP",
        img_b64=fake_b64,
    )
    assert "data:image/jpeg;base64," in html
    assert fake_b64 in html
