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
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"subject": "Test subject", "body_text": "Hola María, texto del email."}'
                )
            )
        ]
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
