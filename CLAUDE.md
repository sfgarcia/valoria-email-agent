# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run Streamlit app
uv run streamlit run app.py

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_agent.py::test_generate_email_returns_dict_with_required_keys

# Lint / format
uv run ruff check .
uv run ruff format .

# Generate synthetic CSV for testing
uv run python generate_csv.py   # writes data/clientes_prueba.csv
```

## Architecture

The app is a 4-step Streamlit wizard (`app.py`):

1. **Config** — user selects a product and uploads a customer CSV
2. **Generate** — iterates each CSV row calling `agent.generate_email()` via Groq
3. **Preview** — shows generated emails grouped by RFM segment, editable subjects
4. **Gmail** — OAuth2 flow then bulk-creates Gmail drafts

**Module responsibilities:**

- `agent.py` — `generate_email(row, producto, api_key)` calls Groq (`llama-3.3-70b-versatile`) with a structured JSON prompt, maps segment → CTA, and delegates HTML rendering to `email_template.py`
- `email_template.py` — `render_html()` produces inline-CSS branded email HTML; `load_image_b64()` embeds product images from `images/` as base64
- `gmail_client.py` — `get_gmail_service()` runs OAuth2 (opens browser, scope: `gmail.compose`); `create_draft()` sends MIME messages to the Gmail Drafts API
- `generate_csv.py` — one-shot script that generates `data/clientes_prueba.csv` with 50 synthetic customers across 5 RFM segments

**Required CSV columns:** `cliente_id`, `nombre`, `email`, `segmento`, `rfm_recencia`, `rfm_frecuencia`, `rfm_monto`, `ultimo_producto`, `monto_total_historico`, `dias_sin_compra`, `ciudad`

**RFM segments:** `VIP`, `Familias`, `Gen-Z`, `Carrito`, `Dormidos` — each has distinct tone rules in the system prompt and a different CTA color/URL.

## Secrets

Copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` and fill in:

```toml
GROQ_API_KEY = "gsk_..."

[google_oauth]
client_id = "....apps.googleusercontent.com"
client_secret = "GOCSPX-..."
```

For Streamlit Cloud deployment, add these same keys under **App Settings → Secrets**.
