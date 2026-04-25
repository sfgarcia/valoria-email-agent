# Valoria Email Agent — Design Spec
**Date:** 2026-04-25  
**Project:** MBA UC Taller de Agentes — Actividad 2 (Caso Marketing)  
**Deadline:** 2026-05-08

---

## Contexto y Problema

Valoria (retail lifestyle/fashion) envió un email genérico de descuentos masivos a sus 100,000 clientes. El resultado fue una disonancia de marca severa: clientes VIP se sintieron devaluados, clientes dormidos ignoraron el mensaje, carritos abandonados no fueron recuperados. La solución es un agente de IA que genera emails hiper-personalizados por segmento usando el historial de compras de cada cliente y el tono de marca de Valoria.

---

## Visión de la Solución

Herramienta Streamlit operada por el equipo de marketing de Valoria. El operador sube un CSV de clientes, selecciona el producto a promover, y el agente genera un email HTML personalizado para cada cliente según su segmento RFM. Los emails se guardan como borradores en Gmail listos para enviar.

---

## Flujo Principal (4 pasos)

```
[1] Configurar Campaña
    → Seleccionar producto (Eco-Trek / Urban Flow / Lumina Restore)
    → Subir CSV de clientes

[2] Agente Claude genera emails
    → 1 prompt por cliente con datos individuales
    → Sistema prompt incluye reglas por segmento + tono Valoria
    → Output: JSON { subject, body_html, segmento, to, nombre }

[3] Preview & Edición
    → Tabs por segmento (VIP / Familias / Gen-Z / Carrito / Dormidos)
    → Email renderizado + opción editar subject o body
    → Contador de emails por segmento

[4] Aprobar → Gmail Drafts
    → OAuth2 Google (usuario autoriza con su cuenta Gmail)
    → Gmail API crea draft por cada cliente aprobado
    → Confirmación con link a Gmail
```

---

## Stack Técnico

| Capa | Tecnología |
|---|---|
| Frontend | Streamlit (Python) |
| IA | Groq API — `llama-3.3-70b-versatile` (free tier) |
| Email API | Gmail API v1 + OAuth2 (`google-auth-oauthlib`) |
| Datos | polars (CSV parsing) |
| Deploy | Streamlit Cloud (link público compartible) |
| Secrets | Streamlit secrets (GROQ_API_KEY, Google OAuth creds) |

---

## Segmentos y Tono de Email

| Segmento | RFM Típico | Tono | Restricciones |
|---|---|---|---|
| VIP Campeones | 5-5-5 | Exclusividad, acceso early, prestigio | **Nunca** descuentos genéricos |
| Familias (Leales Potenciales) | 3-4-2 | Valor, durabilidad, economía familiar | Destacar precio por uso/vida útil |
| Gen-Z / Nómadas Digitales | 4-3-2 | Lifestyle, tendencia, tono conversacional | Subject visual y disruptivo |
| Abandonadores de Carrito | 5-1-1 | Urgencia suave, incentivo específico | Mencionar producto exacto del carrito |
| Dormidos / Hibernación | 1-1-1 | Emotivo, reencuentro, nostalgia de marca | Reconocer ausencia explícitamente |

---

## Productos a Promover

| Producto | Precio | Segmentos naturales |
|---|---|---|
| Chaqueta Eco-Trek | $295 | VIP, Familias |
| Mochila Urban Flow | $140 | Gen-Z, Carrito |
| Kit Lumina Restore | $85 | Dormidos, Familias, cross-sell |

---

## Estructura de Archivos

```
Tarea 2/
├── app.py                        # Streamlit app principal (4 steps UI)
├── agent.py                      # Claude API — generación de emails
├── gmail_client.py               # OAuth2 + Gmail draft creation
├── email_template.py             # HTML template con branding Valoria
├── data/
│   └── clientes_prueba.csv       # 50 clientes sintéticos (5 segmentos x ~10)
├── requirements.txt
├── .streamlit/
│   └── secrets.toml              # ANTHROPIC_API_KEY, Google OAuth
└── docs/superpowers/specs/
    └── 2026-04-25-valoria-email-agent-design.md
```

---

## CSV de Entrada (campos)

```csv
cliente_id, nombre, email, segmento, rfm_recencia, rfm_frecuencia, rfm_monto,
ultimo_producto, monto_total_historico, dias_sin_compra, ciudad
```

El CSV de prueba (`clientes_prueba.csv`) se genera sintéticamente con 50 filas distribuidas entre los 5 segmentos, con datos coherentes para cada perfil.

---

## Email HTML Template

Template base con:
- Header: logo Valoria (placeholder SVG) + colores marca (`#1a1a2e` / `#7c3aed`)
- **Imagen del producto**: `<img>` con ruta local base64-embebida o URL pública del banco de imágenes
- Body: texto personalizado generado por Groq (subject + 2-3 párrafos)
- CTA button: texto dinámico según segmento
- Footer: "© Valoria · Sostenible por diseño" + unsubscribe link placeholder

Groq genera el **contenido** (subject + body text); el template envuelve el estilo visual.

## Banco de Imágenes de Productos

Imágenes generadas con IA (Pollinations.ai — free, sin API key) y almacenadas en `images/`:

| Archivo | Producto | Prompt generación |
|---|---|---|
| `images/eco-trek.jpg` | Chaqueta Eco-Trek | premium sustainable outdoor jacket minimal dark aesthetic ocean recycled fabric |
| `images/urban-flow.jpg` | Mochila Urban Flow | smart urban backpack tech streetwear minimal black photography studio |
| `images/lumina-restore.jpg` | Kit Lumina Restore | wellness spa kit botanical serenity minimal packaging essential oils |

Script de generación: `generate_images.py` (one-shot, descarga y guarda en `images/`).
El template embebe la imagen como `data:image/jpeg;base64,...` para que funcione en cualquier cliente de email.

---

## Lógica del Agente (agent.py)

Usa `groq` Python SDK. API key embebida en Streamlit secrets. Free tier soporta ~14,400 req/día con `llama-3.3-70b-versatile`.

```python
# Por cada fila del CSV:
system_prompt = """
Eres el agente de marketing de Valoria, marca premium de lifestyle sostenible.
Generas emails hiper-personalizados según el segmento del cliente.
Tono de marca: aspiracional, sofisticado, auténtico. Nunca genérico.
Reglas:
- VIP: exclusividad, early access, reconocimiento de lealtad. Sin descuentos.
- Familias: valor demostrable, durabilidad, economía inteligente.
- Gen-Z: conversacional, trend-forward, conectado a cultura visual.
- Carrito: menciona el producto específico, reduce fricción, incentivo suave.
- Dormidos: reconoce su ausencia, emotivo, muestra que la marca evolucionó.
Output: JSON estricto { "subject": "...", "body_text": "..." }
"""

user_prompt = f"""
Cliente: {row['nombre']}
Segmento: {row['segmento']}
Último producto: {row['ultimo_producto']}
Días sin compra: {row['dias_sin_compra']}
Monto histórico: ${row['monto_total_historico']}
Producto a promover: {producto_seleccionado}
Genera el email personalizado.
"""
```

---

## Gmail Integration (gmail_client.py)

- OAuth2 flow con `google-auth-oauthlib` (consent screen en browser)
- Scope: `gmail.compose` (mínimo necesario)
- `create_draft(to, subject, body_html)` → Gmail API `users.drafts.create`
- Para PoC: 1 draft de prueba primero, luego batch completo

---

## Datos Sintéticos (clientes_prueba.csv)

50 filas generadas con Python/Faker:
- 5 VIP (RFM 5-5-5, ciudades premium, montos altos)
- 12 Familias (RFM 3-4-2, compras estacionales)
- 15 Gen-Z (RFM 4-3-2, ciudades jóvenes, montos moderados)
- 10 Carrito (RFM 5-1-1, última visita reciente)
- 8 Dormidos (RFM 1-1-1, sin compras 12-24 meses)

---

## Verificación / Demo

1. Correr `streamlit run app.py` local
2. Subir `clientes_prueba.csv`, seleccionar "Eco-Trek"
3. Verificar que se generan emails diferenciados por segmento
4. Verificar que VIP no recibe copy de descuentos
5. Autorizar OAuth Gmail, crear 1 draft de prueba
6. Confirmar draft aparece en Gmail
7. Deploy en Streamlit Cloud → obtener link público

---

## Entregables Finales (para Actividad 2)

1. **Link Streamlit Cloud** — plataforma funcional
2. **Documento** — visión, funcionalidades, impacto, desafíos, escalamiento
3. **Video 3 min** — demo del agente en vivo
