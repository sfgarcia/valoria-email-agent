# Valoria Email Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Streamlit app que genera emails HTML hiper-personalizados por segmento RFM usando Groq (llama-3.3-70b) y los guarda como borradores en Gmail.

**Architecture:** El usuario sube un CSV con datos de clientes Valoria → el agente Groq genera un email HTML personalizado por cliente según su segmento → el usuario revisa/edita en preview → aprueba y se crean drafts en Gmail vía OAuth2.

**Tech Stack:** Python 3.12, uv, Streamlit, Groq SDK, google-auth-oauthlib, google-api-python-client, polars, pytest, ruff

---

## File Map

```
Tarea 2/
├── app.py                    # Streamlit UI principal (4 steps con session_state)
├── agent.py                  # Groq API — generate_email(row, producto) → dict
├── email_template.py         # render_html(body_text, cta_url, segmento, img_b64) → str HTML
├── gmail_client.py           # OAuth2 + create_draft(service, to, subject, body_html)
├── generate_csv.py           # Script one-shot: genera data/clientes_prueba.csv
├── generate_images.py        # Script one-shot: genera images/ con Pollinations.ai
├── data/
│   └── clientes_prueba.csv   # 50 clientes sintéticos
├── images/
│   ├── eco-trek.jpg          # AI-generated (Pollinations.ai)
│   ├── urban-flow.jpg        # AI-generated
│   └── lumina-restore.jpg    # AI-generated
├── tests/
│   ├── test_agent.py
│   ├── test_email_template.py
│   └── test_gmail_client.py
├── .streamlit/
│   ├── secrets.toml.example
│   └── secrets.toml          # NO commitear
├── pyproject.toml
└── requirements.txt
```

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `.streamlit/secrets.toml.example`
- Create: `.gitignore`

- [ ] **Step 1: Inicializar proyecto con uv**

```bash
cd "c:/Users/sfgarcia/Documents/MBA UC/2026-Q1/Taller de creación de agentes/Tarea 2"
uv init --no-readme
uv add streamlit groq google-auth-oauthlib google-api-python-client polars pytest ruff
```

Expected: `pyproject.toml` creado, `.venv/` creado.

- [ ] **Step 2: Crear requirements.txt para Streamlit Cloud**

```bash
uv pip compile pyproject.toml -o requirements.txt
```

Si el comando falla, crear manualmente:

```
streamlit>=1.35.0
groq>=0.9.0
google-auth-oauthlib>=1.2.0
google-api-python-client>=2.130.0
polars>=0.20.0
```

- [ ] **Step 3: Crear .streamlit/secrets.toml.example**

```bash
mkdir -p .streamlit
```

Contenido de `.streamlit/secrets.toml.example`:
```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"

[google_oauth]
client_id = "xxxx.apps.googleusercontent.com"
client_secret = "GOCSPX-xxxxxxxxxx"
```

- [ ] **Step 4: Crear .gitignore**

```
.venv/
.streamlit/secrets.toml
data/*.csv
__pycache__/
*.pyc
.env
token.json
credentials.json
```

- [ ] **Step 5: Crear estructura de directorios**

```bash
mkdir -p data tests .streamlit
touch app.py agent.py email_template.py gmail_client.py generate_csv.py
touch tests/__init__.py tests/test_agent.py tests/test_email_template.py tests/test_gmail_client.py
```

- [ ] **Step 6: Commit**

```bash
git init
git add pyproject.toml requirements.txt .gitignore .streamlit/secrets.toml.example
git commit -m "chore: project setup — streamlit + groq + gmail stack"
```

---

## Task 2: CSV de Datos Sintéticos

**Files:**
- Create: `generate_csv.py`
- Create: `data/clientes_prueba.csv`

- [ ] **Step 1: Escribir generate_csv.py**

```python
"""Script one-shot para generar CSV de clientes sintéticos de Valoria."""
import polars as pl
import random

random.seed(42)

SEGMENTOS = {
    "VIP": {
        "count": 5,
        "rfm": [(5, 5, 5), (5, 5, 4), (4, 5, 5)],
        "ciudades": ["Santiago", "Las Condes", "Providencia"],
        "montos": (800, 3000),
        "dias_sin_compra": (1, 30),
        "productos": ["Chaqueta Eco-Trek", "Mochila Urban Flow"],
    },
    "Familias": {
        "count": 12,
        "rfm": [(3, 4, 2), (3, 3, 2), (4, 4, 2)],
        "ciudades": ["Maipú", "Pudahuel", "La Florida", "Viña del Mar"],
        "montos": (200, 600),
        "dias_sin_compra": (30, 90),
        "productos": ["Kit Lumina Restore", "Chaqueta Eco-Trek"],
    },
    "Gen-Z": {
        "count": 15,
        "rfm": [(4, 3, 2), (5, 2, 2), (4, 3, 1)],
        "ciudades": ["Valparaíso", "Santiago Centro", "Ñuñoa", "Concepción"],
        "montos": (100, 350),
        "dias_sin_compra": (7, 60),
        "productos": ["Mochila Urban Flow", "Kit Lumina Restore"],
    },
    "Carrito": {
        "count": 10,
        "rfm": [(5, 1, 1), (5, 2, 1)],
        "ciudades": ["Santiago", "Providencia", "Vitacura"],
        "montos": (0, 150),
        "dias_sin_compra": (1, 3),
        "productos": ["Mochila Urban Flow", "Chaqueta Eco-Trek"],
    },
    "Dormidos": {
        "count": 8,
        "rfm": [(1, 1, 1), (1, 1, 2), (2, 1, 1)],
        "ciudades": ["Temuco", "Puerto Montt", "Antofagasta", "Iquique"],
        "montos": (50, 300),
        "dias_sin_compra": (365, 730),
        "productos": ["Kit Lumina Restore", "Chaqueta Eco-Trek"],
    },
}

NOMBRES = [
    "María González", "Juan Pérez", "Catalina López", "Andrés Martínez",
    "Valentina Rodríguez", "Diego Sánchez", "Sofía Fernández", "Matías Torres",
    "Isidora Ramírez", "Felipe Vargas", "Camila Morales", "Sebastián Jiménez",
    "Antonia Castro", "Nicolás Reyes", "Amanda Flores", "Rodrigo Díaz",
    "Fernanda Herrera", "Benjamín Medina", "Constanza Rojas", "Ignacio Vega",
    "Daniela Muñoz", "Cristóbal Pizarro", "Paula Gutiérrez", "Tomás Aguilera",
    "Javiera Riquelme", "Alexis Fuentes", "Renata Molina", "Vicente Bravo",
    "Pilar Campos", "Gabriel Espinoza", "Magdalena Cruz", "Emilio Navarro",
    "Francisca Ríos", "Alonso Ortiz", "Trinidad Cárdenas", "Simón Araya",
    "Valentina Soto", "Marcelo Contreras", "Rocío Peña", "Esteban Jara",
    "Martina Leal", "Pablo Cerda", "Carla Ibáñez", "Lucas Tapia",
    "Agustina Vergara", "Eduardo Ponce", "Lorena Valenzuela", "Maximiliano Fuentealba",
    "Ximena Cuevas", "Ricardo Paredes",
]


def generate_email_address(nombre: str, idx: int) -> str:
    first = nombre.split()[0].lower()
    first = first.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    return f"{first}.{idx:03d}@ejemplo.cl"


def build_rows() -> list[dict]:
    rows = []
    nombre_pool = iter(NOMBRES)
    idx = 1

    for segmento, cfg in SEGMENTOS.items():
        for _ in range(cfg["count"]):
            nombre = next(nombre_pool)
            rfm = random.choice(cfg["rfm"])
            monto = round(random.uniform(*cfg["montos"]), 2)
            dias = random.randint(*cfg["dias_sin_compra"])
            rows.append({
                "cliente_id": f"CLI{idx:04d}",
                "nombre": nombre,
                "email": generate_email_address(nombre, idx),
                "segmento": segmento,
                "rfm_recencia": rfm[0],
                "rfm_frecuencia": rfm[1],
                "rfm_monto": rfm[2],
                "ultimo_producto": random.choice(cfg["productos"]),
                "monto_total_historico": monto,
                "dias_sin_compra": dias,
                "ciudad": random.choice(cfg["ciudades"]),
            })
            idx += 1

    return rows


if __name__ == "__main__":
    rows = build_rows()
    df = pl.DataFrame(rows)
    df.write_csv("data/clientes_prueba.csv")
    print(f"CSV generado: {len(rows)} clientes")
    print(df.group_by("segmento").len().sort("segmento"))
```

- [ ] **Step 2: Ejecutar script**

```bash
uv run python generate_csv.py
```

Expected output:
```
CSV generado: 50 clientes
shape: (5, 2)
┌──────────┬─────┐
│ segmento ┆ len │
╞══════════╪═════╡
│ Carrito  ┆ 10  │
│ Dormidos ┆ 8   │
│ Familias ┆ 12  │
│ Gen-Z    ┆ 15  │
│ VIP      ┆ 5   │
└──────────┴─────┘
```

- [ ] **Step 3: Verificar CSV**

```bash
uv run python -c "import polars as pl; print(pl.read_csv('data/clientes_prueba.csv').head(3))"
```

Expected: tabla con 3 filas con todas las columnas.

- [ ] **Step 4: Commit**

```bash
git add generate_csv.py
git commit -m "feat: synthetic CSV generator — 50 Valoria clients across 5 segments"
```

---

## Task 2b: Banco de Imágenes de Productos (AI-Generated)

**Files:**
- Create: `generate_images.py`
- Create: `images/eco-trek.jpg`
- Create: `images/urban-flow.jpg`
- Create: `images/lumina-restore.jpg`

- [ ] **Step 1: Crear directorio images/**

```bash
mkdir -p images
```

- [ ] **Step 2: Escribir generate_images.py**

```python
"""Script one-shot: genera imágenes de productos Valoria con Pollinations.ai."""
import urllib.request
import pathlib
import time

PRODUCTS = {
    "eco-trek.jpg": (
        "premium sustainable outdoor jacket dark minimal aesthetic, "
        "ocean recycled fabric, professional product photography, "
        "black background, luxury fashion editorial"
    ),
    "urban-flow.jpg": (
        "smart urban backpack tech streetwear minimal black, "
        "professional product photography, studio lighting, "
        "modern lifestyle accessory, dark background"
    ),
    "lumina-restore.jpg": (
        "wellness spa recovery kit botanical serenity, "
        "essential oils mist silk eye mask herbal teas, "
        "minimal packaging white background, luxury self-care product photography"
    ),
}

BASE_URL = "https://image.pollinations.ai/prompt/{prompt}?width=600&height=400&nologo=true&model=flux"
OUTPUT_DIR = pathlib.Path("images")
OUTPUT_DIR.mkdir(exist_ok=True)


def download_image(filename: str, prompt: str) -> None:
    encoded = urllib.parse.quote(prompt)
    url = BASE_URL.format(prompt=encoded)
    dest = OUTPUT_DIR / filename
    print(f"Generando {filename}...")
    urllib.request.urlretrieve(url, dest)
    size_kb = dest.stat().st_size // 1024
    print(f"  ✓ Guardado: {dest} ({size_kb} KB)")


if __name__ == "__main__":
    import urllib.parse
    for filename, prompt in PRODUCTS.items():
        download_image(filename, prompt)
        time.sleep(2)  # evitar rate limit
    print("\nBanco de imágenes listo en images/")
```

- [ ] **Step 3: Ejecutar script**

```bash
uv run python generate_images.py
```

Expected:
```
Generando eco-trek.jpg...
  ✓ Guardado: images/eco-trek.jpg (XX KB)
Generando urban-flow.jpg...
  ✓ Guardado: images/urban-flow.jpg (XX KB)
Generando lumina-restore.jpg...
  ✓ Guardado: images/lumina-restore.jpg (XX KB)

Banco de imágenes listo en images/
```

- [ ] **Step 4: Verificar imágenes visualmente**

```bash
# Windows: abrir las 3 imágenes
start images/eco-trek.jpg
start images/urban-flow.jpg
start images/lumina-restore.jpg
```

Si alguna imagen no se ve bien, re-ejecutar `generate_images.py` (Pollinations genera variaciones distintas cada vez).

- [ ] **Step 5: Commit**

```bash
git add generate_images.py images/
git commit -m "feat: AI-generated product image bank via Pollinations.ai (Flux)"
```

---

## Task 3: HTML Email Template

**Files:**
- Create: `email_template.py`
- Create: `tests/test_email_template.py`

- [ ] **Step 1: Escribir test**

```python
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
    fake_b64 = "iVBORw0KGgoAAAANS"  # fragmento base64 falso
    html = render_html(
        body_text="Mensaje.",
        cta_text="CTA",
        cta_url="https://valoria.com",
        segmento="VIP",
        img_b64=fake_b64,
    )
    assert "data:image/jpeg;base64," in html
    assert fake_b64 in html
```

- [ ] **Step 2: Ejecutar test — verificar que falla**

```bash
uv run pytest tests/test_email_template.py -v
```

Expected: `ImportError` o `ModuleNotFoundError` porque `email_template.py` está vacío.

- [ ] **Step 3: Implementar email_template.py**

```python
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


def render_html(body_text: str, cta_text: str, cta_url: str, segmento: str, img_b64: str | None) -> str:
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
        if img_b64 else ""
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
```

- [ ] **Step 4: Ejecutar tests — verificar que pasan**

```bash
uv run pytest tests/test_email_template.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add email_template.py tests/test_email_template.py
git commit -m "feat: Valoria HTML email template with segment-aware CTA colors"
```

---

## Task 4: Groq Email Agent

**Files:**
- Create: `agent.py`
- Create: `tests/test_agent.py`

- [ ] **Step 1: Escribir tests**

```python
# tests/test_agent.py
from unittest.mock import MagicMock, patch
from agent import generate_email, SYSTEM_PROMPT, _build_user_prompt

def test_build_user_prompt_includes_key_fields():
    row = {
        "nombre": "María González",
        "segmento": "VIP",
        "ultimo_producto": "Chaqueta Eco-Trek",
        "dias_sin_compra": 15,
        "monto_total_historico": 1200.0,
        "ciudad": "Las Condes",
    }
    prompt = _build_user_prompt(row, "Chaqueta Eco-Trek")
    assert "María González" in prompt
    assert "VIP" in prompt
    assert "Chaqueta Eco-Trek" in prompt
    assert "15" in prompt

def test_system_prompt_contains_segment_rules():
    assert "VIP" in SYSTEM_PROMPT
    assert "Dormidos" in SYSTEM_PROMPT
    assert "Carrito" in SYSTEM_PROMPT
    assert "descuentos" in SYSTEM_PROMPT.lower()

@patch("agent.Groq")
def test_generate_email_returns_dict_with_required_keys(mock_groq_cls):
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"subject": "Test subject", "body_text": "Hola María, texto del email."}'))]
    )
    row = {
        "nombre": "María González",
        "email": "maria@ejemplo.cl",
        "segmento": "VIP",
        "ultimo_producto": "Chaqueta Eco-Trek",
        "dias_sin_compra": 15,
        "monto_total_historico": 1200.0,
        "ciudad": "Las Condes",
    }
    result = generate_email(row, "Chaqueta Eco-Trek", api_key="fake-key")
    assert "subject" in result
    assert "body_html" in result
    assert "to" in result
    assert result["to"] == "maria@ejemplo.cl"
    assert "<" in result["body_html"]  # es HTML
```

- [ ] **Step 2: Ejecutar tests — verificar que fallan**

```bash
uv run pytest tests/test_agent.py -v
```

Expected: `ImportError` porque `agent.py` está vacío.

- [ ] **Step 3: Implementar agent.py**

```python
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
```

- [ ] **Step 4: Ejecutar tests — verificar que pasan**

```bash
uv run pytest tests/test_agent.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Smoke test manual con API key real**

Crea `.streamlit/secrets.toml` con tu `GROQ_API_KEY` real:
```toml
GROQ_API_KEY = "gsk_tu_clave_aqui"
```

Luego ejecuta:
```bash
uv run python -c "
import polars as pl, tomllib, pathlib
from agent import generate_email
secrets = tomllib.loads(pathlib.Path('.streamlit/secrets.toml').read_text())
df = pl.read_csv('data/clientes_prueba.csv')
row = df.filter(pl.col('segmento') == 'VIP').row(0, named=True)
result = generate_email(row, 'Chaqueta Eco-Trek', secrets['GROQ_API_KEY'])
print('Subject:', result['subject'])
print('HTML length:', len(result['body_html']))
"
```

Expected: subject generado + HTML con >500 chars.

- [ ] **Step 6: Commit**

```bash
git add agent.py tests/test_agent.py
git commit -m "feat: Groq email agent with segment-aware prompting (llama-3.3-70b)"
```

---

## Task 5: Gmail Client

**Files:**
- Create: `gmail_client.py`
- Create: `tests/test_gmail_client.py`

- [ ] **Step 1: Escribir tests**

```python
# tests/test_gmail_client.py
from unittest.mock import MagicMock, patch
from gmail_client import create_draft, build_gmail_message

def test_build_gmail_message_encodes_correctly():
    import base64
    msg_bytes = build_gmail_message(
        to="test@example.com",
        subject="Test Subject",
        body_html="<p>Hello</p>",
    )
    # debe ser un dict con clave 'raw'
    assert "raw" in msg_bytes
    # raw debe ser base64url decodificable
    decoded = base64.urlsafe_b64decode(msg_bytes["raw"] + "==")
    assert b"test@example.com" in decoded
    assert b"Test Subject" in decoded

def test_create_draft_calls_gmail_api():
    mock_service = MagicMock()
    mock_service.users().drafts().create().execute.return_value = {"id": "draft123"}

    result = create_draft(
        service=mock_service,
        to="cliente@ejemplo.cl",
        subject="Email Valoria",
        body_html="<p>Hola</p>",
    )

    mock_service.users().drafts().create.assert_called_once()
    assert result["id"] == "draft123"
```

- [ ] **Step 2: Ejecutar tests — verificar que fallan**

```bash
uv run pytest tests/test_gmail_client.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implementar gmail_client.py**

```python
"""Gmail API client para creación de borradores."""
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def get_gmail_service(client_id: str, client_secret: str) -> object:
    """Inicia OAuth2 flow y retorna servicio Gmail autenticado.

    Abre el browser del usuario para autorización en primera ejecución.
    """
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)
    return build("gmail", "v1", credentials=creds)


def build_gmail_message(to: str, subject: str, body_html: str) -> dict:
    """Construye mensaje MIME codificado en base64url para Gmail API."""
    msg = MIMEMultipart("alternative")
    msg["to"] = to
    msg["subject"] = subject
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw}


def create_draft(service: object, to: str, subject: str, body_html: str) -> dict:
    """Crea un borrador en Gmail del usuario autenticado.

    Args:
        service: Servicio Gmail autenticado (de get_gmail_service).
        to: Email del destinatario.
        subject: Asunto del email.
        body_html: Cuerpo HTML del email.

    Returns:
        Dict con 'id' del draft creado.
    """
    message = build_gmail_message(to, subject, body_html)
    draft = service.users().drafts().create(
        userId="me",
        body={"message": message},
    ).execute()
    return draft
```

- [ ] **Step 4: Ejecutar tests — verificar que pasan**

```bash
uv run pytest tests/test_gmail_client.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add gmail_client.py tests/test_gmail_client.py
git commit -m "feat: Gmail OAuth2 client with draft creation"
```

---

## Task 6: Streamlit App

**Files:**
- Create: `app.py`

> No hay tests unitarios para Streamlit UI — se verifica manualmente. La lógica de negocio ya está testeada en Tasks 3-5.

- [ ] **Step 1: Implementar app.py**

```python
"""Valoria Email Agent — Streamlit App."""
import polars as pl
import streamlit as st

from agent import generate_email
from gmail_client import create_draft, get_gmail_service

PRODUCTOS = {
    "Chaqueta Eco-Trek ($295)": "Chaqueta Eco-Trek",
    "Mochila Urban Flow ($140)": "Mochila Urban Flow",
    "Kit Lumina Restore ($85)": "Kit Lumina Restore",
}

SEGMENTO_ORDEN = ["VIP", "Familias", "Gen-Z", "Carrito", "Dormidos"]


def init_session():
    defaults = {
        "step": 1,
        "df": None,
        "producto": None,
        "emails_generados": [],
        "gmail_service": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def step1_config():
    st.header("⚙️ Paso 1 — Configurar Campaña")

    producto_label = st.selectbox("Producto a promover", list(PRODUCTOS.keys()))
    archivo = st.file_uploader("Subir CSV de clientes", type=["csv"])

    if archivo and st.button("🚀 Generar Emails", type="primary"):
        df = pl.read_csv(archivo)
        st.session_state.df = df
        st.session_state.producto = PRODUCTOS[producto_label]
        st.session_state.step = 2
        st.rerun()


def step2_generate():
    st.header("🤖 Paso 2 — Generando Emails...")

    df = st.session_state.df
    producto = st.session_state.producto
    api_key = st.secrets["GROQ_API_KEY"]

    emails = []
    progress = st.progress(0, text="Iniciando...")
    total = len(df)

    for i, row in enumerate(df.iter_rows(named=True)):
        progress.progress((i + 1) / total, text=f"Generando email para {row['nombre']}...")
        email = generate_email(row, producto, api_key)
        emails.append(email)

    st.session_state.emails_generados = emails
    st.session_state.step = 3
    st.rerun()


def step3_preview():
    st.header("👁️ Paso 3 — Preview & Edición")

    emails = st.session_state.emails_generados
    emails_por_segmento = {}
    for e in emails:
        emails_por_segmento.setdefault(e["segmento"], []).append(e)

    tabs = st.tabs([f"{s} ({len(emails_por_segmento.get(s, []))})" for s in SEGMENTO_ORDEN if s in emails_por_segmento])

    segmentos_con_data = [s for s in SEGMENTO_ORDEN if s in emails_por_segmento]
    for tab, segmento in zip(tabs, segmentos_con_data):
        with tab:
            for idx, email in enumerate(emails_por_segmento[segmento]):
                with st.expander(f"📧 {email['nombre']} — {email['subject']}", expanded=(idx == 0)):
                    email["subject"] = st.text_input(
                        "Asunto", value=email["subject"],
                        key=f"sub_{segmento}_{idx}"
                    )
                    st.components.v1.html(email["body_html"], height=400, scrolling=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver"):
            st.session_state.step = 1
            st.session_state.emails_generados = []
            st.rerun()
    with col2:
        if st.button("✅ Aprobar y Crear Borradores en Gmail →", type="primary"):
            st.session_state.step = 4
            st.rerun()


def step4_gmail():
    st.header("📧 Paso 4 — Crear Borradores en Gmail")

    emails = st.session_state.emails_generados
    st.info(f"Se crearán **{len(emails)} borradores** en tu Gmail.")

    st.subheader("Resumen por segmento")
    from collections import Counter
    counts = Counter(e["segmento"] for e in emails)
    for seg in SEGMENTO_ORDEN:
        if seg in counts:
            st.write(f"- **{seg}**: {counts[seg]} emails")

    if st.session_state.gmail_service is None:
        st.warning("Necesitas autorizar acceso a Gmail.")
        if st.button("🔐 Conectar con Gmail"):
            creds = st.secrets["google_oauth"]
            service = get_gmail_service(creds["client_id"], creds["client_secret"])
            st.session_state.gmail_service = service
            st.rerun()
    else:
        if st.button("📬 Crear todos los borradores", type="primary"):
            service = st.session_state.gmail_service
            progress = st.progress(0)
            errores = []
            for i, email in enumerate(emails):
                try:
                    create_draft(service, email["to"], email["subject"], email["body_html"])
                except Exception as e:
                    errores.append(f"{email['nombre']}: {e}")
                progress.progress((i + 1) / len(emails))

            if errores:
                st.error(f"{len(errores)} errores:\n" + "\n".join(errores))
            else:
                st.success(f"✅ {len(emails)} borradores creados exitosamente en Gmail.")
                st.balloons()
                st.markdown("[Ir a Gmail →](https://mail.google.com/mail/u/0/#drafts)")

        if st.button("← Volver al Preview"):
            st.session_state.step = 3
            st.rerun()


def main():
    st.set_page_config(
        page_title="Valoria Email Agent",
        page_icon="✉️",
        layout="wide",
    )
    st.title("✉️ Valoria Email Agent")
    st.caption("Generación hiper-personalizada de emails por segmento RFM")

    init_session()

    step = st.session_state.step
    steps_label = ["1. Configurar", "2. Generar", "3. Preview", "4. Gmail"]
    st.progress((step - 1) / 3, text=f"Paso {step} de 4 — {steps_label[step - 1]}")
    st.divider()

    if step == 1:
        step1_config()
    elif step == 2:
        step2_generate()
    elif step == 3:
        step3_preview()
    elif step == 4:
        step4_gmail()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Correr app localmente**

```bash
uv run streamlit run app.py
```

Expected: browser abre en `http://localhost:8501` con UI de Valoria.

- [ ] **Step 3: Smoke test manual — flujo completo**

1. Seleccionar "Chaqueta Eco-Trek ($295)"
2. Subir `data/clientes_prueba.csv`
3. Click "Generar Emails" → esperar generación (~2-3 min para 50 emails)
4. Verificar que cada segmento tiene emails diferenciados en tono
5. Verificar que VIP no recibe copy de descuentos
6. Revisar un email en preview (HTML renderizado)
7. (Opcional) Conectar Gmail y crear 1 draft de prueba

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: Streamlit 4-step UI — config, generate, preview, Gmail drafts"
```

---

## Task 7: Deploy en Streamlit Cloud

**Files:**
- No hay archivos nuevos — solo configuración en Streamlit Cloud UI.

- [ ] **Step 1: Subir código a GitHub**

```bash
# Si no tienes repo aún:
gh repo create valoria-email-agent --private --source=. --push

# Si ya tienes repo:
git push origin main
```

- [ ] **Step 2: Crear app en Streamlit Cloud**

1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Seleccionar repo `valoria-email-agent`, branch `main`, file `app.py`
4. Click "Advanced settings" → agregar secrets:

```toml
GROQ_API_KEY = "gsk_tu_clave_real"

[google_oauth]
client_id = "xxxx.apps.googleusercontent.com"
client_secret = "GOCSPX-xxxxxxxxxx"
```

5. Click "Deploy"

- [ ] **Step 3: Verificar deploy**

- App carga sin errores en la URL pública de Streamlit Cloud
- Subir `clientes_prueba.csv` y verificar que genera emails
- Copiar URL pública — este es el entregable (i) de la actividad

- [ ] **Step 4: Commit final**

```bash
git tag v1.0.0-poc
git push origin main --tags
```

---

## Task 8: Suite Completa de Tests

- [ ] **Step 1: Correr suite completa**

```bash
uv run pytest tests/ -v --tb=short
```

Expected: todos los tests pasan.

- [ ] **Step 2: Lint**

```bash
uv run ruff check . && uv run ruff format --check .
```

Si hay errores:
```bash
uv run ruff check --fix . && uv run ruff format .
git add -u && git commit -m "chore: ruff lint and format fixes"
```

---

## Verificación End-to-End

1. `uv run pytest tests/ -v` → todos pasan
2. `uv run streamlit run app.py` → UI carga correctamente
3. Subir `data/clientes_prueba.csv` + producto "Eco-Trek"
4. Verificar 50 emails generados con tonos diferenciados por segmento
5. Verificar que segmento VIP NO tiene copy de descuentos
6. Verificar que segmento Dormidos tiene tono emotivo de reencuentro
7. Abrir 1 email de cada segmento → HTML renderizado correctamente con branding Valoria
8. Crear 1 draft de prueba en Gmail → aparece en Drafts
9. App funciona en Streamlit Cloud (URL pública)
