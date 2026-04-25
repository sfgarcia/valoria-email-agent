"""Groq LLM agent para generación de emails personalizados Valoria."""
import json
from groq import Groq
from email_template import render_html, load_image_b64

SYSTEM_PROMPT = """Eres el agente de marketing de Valoria, marca premium de lifestyle sostenible.
Generas emails hiper-personalizados en español según el segmento RFM del cliente.
Tono de marca: aspiracional, sofisticado, auténtico, cercano. Nunca genérico.

Reglas obligatorias por segmento:
- VIP (Campeones): tono de exclusividad y reconocimiento. Early access, historias de diseño.
  NUNCA menciones descuentos genéricos ni liquidaciones.
- Familias (Leales Potenciales): destaca valor, durabilidad y economía inteligente a largo plazo.
  Articula cómo el producto resuelve su vida diaria familiar.
- Gen-Z (Nómadas Digitales): tono conversacional, ágil, conectado a tendencias culturales.
  Subject visualmente disruptivo. Conecta el producto con su estilo de vida.
- Carrito (Abandonadores): menciona el producto específico que estuvieron evaluando.
  Reduce la fricción de decisión. Ofrece un incentivo suave (ej: envío gratis).
- Dormidos (Hibernación): reconoce explícitamente su ausencia. Tono emotivo de reencuentro.
  Muestra que Valoria evolucionó. "Hace tiempo que no nos vemos."

Output: JSON estricto con exactamente estas dos claves:
{"subject": "...", "body_text": "..."}

El body_text debe tener 3-4 párrafos separados por \\n\\n. No incluir HTML en body_text.
"""

CTA_MAP = {
    "VIP": ("Acceder Primero", "https://valoria.com/vip-access"),
    "Familias": ("Ver Beneficios", "https://valoria.com/familias"),
    "Gen-Z": ("Explorar Ahora", "https://valoria.com/new-arrivals"),
    "Carrito": ("Completar Compra", "https://valoria.com/carrito"),
    "Dormidos": ("Volver a Valoria", "https://valoria.com/bienvenida"),
}


def _build_user_prompt(row: dict, producto: str) -> str:
    return f"""Cliente: {row['nombre']}
Segmento: {row['segmento']}
Ciudad: {row['ciudad']}
Último producto comprado: {row['ultimo_producto']}
Días sin compra: {row['dias_sin_compra']}
Monto histórico total: ${row['monto_total_historico']:.0f}
Producto a promover en este email: {producto}

Genera el email personalizado para este cliente."""


def generate_email(row: dict, producto: str, api_key: str) -> dict:
    """Genera email personalizado para un cliente usando Groq.

    Args:
        row: Diccionario con datos del cliente (nombre, email, segmento, etc.)
        producto: Nombre del producto a promover.
        api_key: GROQ_API_KEY.

    Returns:
        dict con claves: subject, body_html, to, nombre, segmento
    """
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(row, producto)},
        ],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    raw = response.choices[0].message.content
    parsed = json.loads(raw)

    segmento = row["segmento"]
    cta_text, cta_url = CTA_MAP.get(segmento, ("Ver Más", "https://valoria.com"))
    img_b64 = load_image_b64(producto)

    body_html = render_html(
        body_text=parsed["body_text"],
        cta_text=cta_text,
        cta_url=cta_url,
        segmento=segmento,
        img_b64=img_b64,
    )

    return {
        "subject": parsed["subject"],
        "body_html": body_html,
        "to": row["email"],
        "nombre": row["nombre"],
        "segmento": segmento,
    }
