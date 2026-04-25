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
    "María González",
    "Juan Pérez",
    "Catalina López",
    "Andrés Martínez",
    "Valentina Rodríguez",
    "Diego Sánchez",
    "Sofía Fernández",
    "Matías Torres",
    "Isidora Ramírez",
    "Felipe Vargas",
    "Camila Morales",
    "Sebastián Jiménez",
    "Antonia Castro",
    "Nicolás Reyes",
    "Amanda Flores",
    "Rodrigo Díaz",
    "Fernanda Herrera",
    "Benjamín Medina",
    "Constanza Rojas",
    "Ignacio Vega",
    "Daniela Muñoz",
    "Cristóbal Pizarro",
    "Paula Gutiérrez",
    "Tomás Aguilera",
    "Javiera Riquelme",
    "Alexis Fuentes",
    "Renata Molina",
    "Vicente Bravo",
    "Pilar Campos",
    "Gabriel Espinoza",
    "Magdalena Cruz",
    "Emilio Navarro",
    "Francisca Ríos",
    "Alonso Ortiz",
    "Trinidad Cárdenas",
    "Simón Araya",
    "Valentina Soto",
    "Marcelo Contreras",
    "Rocío Peña",
    "Esteban Jara",
    "Martina Leal",
    "Pablo Cerda",
    "Carla Ibáñez",
    "Lucas Tapia",
    "Agustina Vergara",
    "Eduardo Ponce",
    "Lorena Valenzuela",
    "Maximiliano Fuentealba",
    "Ximena Cuevas",
    "Ricardo Paredes",
]


def generate_email_address(nombre: str, idx: int) -> str:
    first = nombre.split()[0].lower()
    first = (
        first.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
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
            rows.append(
                {
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
                }
            )
            idx += 1

    return rows


if __name__ == "__main__":
    rows = build_rows()
    df = pl.DataFrame(rows)
    df.write_csv("data/clientes_prueba.csv")
    print(f"CSV generado: {len(rows)} clientes")
    print(df.group_by("segmento").len().sort("segmento"))
