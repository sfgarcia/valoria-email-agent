"""HTML email template con branding Valoria."""

CTA_COLORS = {
    "VIP": "#7c3aed",
    "Familias": "#1d4ed8",
    "Gen-Z": "#db2777",
    "Carrito": "#d97706",
    "Dormidos": "#059669",
}

PRODUCT_IMAGES = {
    "Chaqueta Eco-Trek": "images/eco-trek.jpg",
    "Mochila Urban Flow": "images/urban-flow.jpg",
    "Kit Lumina Restore": "images/lumina-restore.jpg",
}


def load_image_b64(producto: str) -> str | None:
    """Carga imagen del producto como base64. Retorna None si no existe."""
    import base64
    import pathlib

    path = pathlib.Path(PRODUCT_IMAGES.get(producto, ""))
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    return None


def render_html(
    body_text: str, cta_text: str, cta_url: str, segmento: str, img_b64: str | None
) -> str:
    """Renderiza email HTML con branding Valoria.

    Args:
        body_text: Texto del cuerpo generado por el agente (puede incluir saltos de línea).
        cta_text: Texto del botón de llamada a la acción.
        cta_url: URL del botón CTA.
        segmento: Segmento del cliente para color del botón.
        img_b64: Imagen del producto en base64 (opcional). Si None, no se incluye imagen.

    Returns:
        String HTML completo del email.
    """
    cta_color = CTA_COLORS.get(segmento, "#7c3aed")
    body_html = body_text.replace("\n", "<br>")
    img_section = (
        f'<img src="data:image/jpeg;base64,{img_b64}" '
        f'style="width:100%;max-height:280px;object-fit:cover;display:block;" alt="Producto Valoria">'
        if img_b64
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{ font-family: Georgia, serif; background: #f4f4f0; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 32px auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
    .header {{ background: #1a1a2e; padding: 24px 32px; display: flex; align-items: center; gap: 12px; }}
    .logo-box {{ width: 32px; height: 32px; background: {cta_color}; border-radius: 6px; display: inline-block; }}
    .brand-name {{ color: white; font-size: 18px; font-weight: bold; letter-spacing: 3px; font-family: Arial, sans-serif; }}
    .product-img {{ width: 100%; max-height: 280px; object-fit: cover; display: block; }}
    .body {{ padding: 36px 32px; color: #1a1a2e; line-height: 1.8; font-size: 15px; }}
    .cta-btn {{ display: inline-block; background: {cta_color}; color: white; padding: 14px 32px; border-radius: 4px; text-decoration: none; font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; letter-spacing: 1px; margin-top: 24px; }}
    .footer {{ background: #f4f4f0; padding: 16px 32px; text-align: center; font-size: 11px; color: #999; font-family: Arial, sans-serif; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <span class="logo-box"></span>
      <span class="brand-name">VALORIA</span>
    </div>
    {img_section}
    <div class="body">
      <p>{body_html}</p>
      <a href="{cta_url}" class="cta-btn">{cta_text}</a>
    </div>
    <div class="footer">
      © 2025 Valoria · Sostenible por diseño<br>
      <a href="#" style="color:#999">Cancelar suscripción</a>
    </div>
  </div>
</body>
</html>"""
