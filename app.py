import json
import random
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Set

import pandas as pd
import streamlit as st


# =========================
# Datos (pizzas + ingredientes)
# =========================
PIZZAS: Dict[str, List[str]] = {
    # Salsa de tomate
    "0 - MARINARA": ["salsa de tomate"],
    "N. 1": ["salsa de tomate", "mozzarella"],
    "SERRANO": ["salsa de tomate", "mozzarella"],
    "N. 15": ["salsa de tomate", "mozzarella", "pepperoni picante"],
    "N. SPICY": ["salsa de tomate picante", "mozzarella", "pepperoni picante"],
    "N. 3": ["salsa de tomate", "mozzarella", "champiñones", "jamón york"],
    "N. 10": ["salsa de tomate", "mozzarella", "carne picada (buey)", "cebolla caramelizada"],
    "CALAMARS": ["calamar en su tinta negra", "mozzarella", "queso brie"],
    "N. THON": ["salsa de tomate", "mozzarella", "atún", "cebolla caramelizada"],
    "N. ANCHOIS": ["salsa de tomate", "mozzarella", "anchoas", "tomates cherry", "alcaparras"],
    "N. 12": ["salsa de tomate", "mozzarella", "queso de cabra", "queso azul"],
    "N. 21": ["salsa de tomate", "mozzarella", "queso brie", "trufa (tofona)"],
    "N. CANILL": ["salsa de tomate", "mozzarella", "panceta a la pimienta", "scamorza (queso ahumado)"],
    "N. CECINA": ["salsa de tomate", "mozzarella", "queso de cabra"],
    "N. 14": ["salsa de tomate", "mozzarella", "champiñones", "alcachofas", "cebolla caramelizada", "tomates cherry"],
    "VEGAN!": ["salsa de tomate", "queso vegano", "champiñones", "alcachofas", "tomates cherry", "cebolla caramelizada"],

    # Nata / crema
    "N. SOBR": ["nata/crema", "mozzarella", "sobrasada", "queso de cabra"],
    "N. AUB, GOR": ["nata/crema", "mozzarella", "berenjena", "gorgonzola"],
    "SAUMON": ["nata/crema", "mozzarella", "salmón"],
    "N. 5": ["nata/crema", "mozzarella", "champiñones", "bacon", "cebolla caramelizada"],
    "N. 19": ["nata/crema", "mozzarella", "bacon", "cebolla caramelizada", "reblochon (tartiflette)"],
    "N. 8": ["nata/crema", "mozzarella", "queso de cabra", "cebolla caramelizada", "tomates cherry"],
    "N. CURRY": ["nata/crema", "curry", "mozzarella", "pollo", "cebolla caramelizada"],

    # Nuevas
    "CEPS (Font d'Argent)": ["nata/crema", "mozzarella", "carne picada (buey)"],
    "LA PORTELLA": ["crema de calabaza", "mozzarella", "gorgonzola"],

    # Pesto
    "MORTA PEST": ["pesto", "mozzarella"],
    "PESTO XERRI": ["pesto", "mozzarella", "tomates cherry"],

    # Pimienta
    "POIVRE": ["salsa a la pimienta", "mozzarella", "champiñones", "carne picada (buey)"],

    # Especial
    "MAGRET": ["mozzarella", "confit de pato", "comté"],
}

# =========================
# Modo difícil: set fijo
# =========================
DIFFICULT_PIZZAS = [
    "POIVRE",
    "MAGRET",
    "CEPS (Font d'Argent)",
    "LA PORTELLA",
    "N. 5",
    "N. 19",
    "N. 8",
    "N. CURRY",
    "N. 21",
    "N. CANILL",
    "N. ANCHOIS",
    "N. CECINA",
    "CALAMARS",
]
DIFFICULT_PIZZAS = [p for p in DIFFICULT_PIZZAS if p in PIZZAS]  # por seguridad


def all_ingredients(pizzas: Dict[str, List[str]]) -> List[str]:
    s: Set[str] = set()
    for ing_list in pizzas.values():
        s.update(ing_list)
    return sorted(s)


INGREDIENTS_MASTER = all_ingredients(PIZZAS)


# =========================
# Progreso / Stats
# =========================
@dataclass
class PizzaStats:
    seen: int = 0
    correct: int = 0
    wrong: int = 0
    last_seen_ts: float = 0.0


def default_stats() -> Dict[str, PizzaStats]:
    return {name: PizzaStats() for name in PIZZAS.keys()}


def serialize_stats(stats: Dict[str, PizzaStats]) -> str:
    payload = {k: asdict(v) for k, v in stats.items()}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def deserialize_stats(text: str) -> Dict[str, PizzaStats]:
    raw = json.loads(text)
    out: Dict[str, PizzaStats] = {}
    for name in PIZZAS.keys():
        if name in raw:
            out[name] = PizzaStats(**raw[name])
        else:
            out[name] = PizzaStats()
    return out


def pick_next_pizza(
    stats: Dict[str, PizzaStats],
    only_wrong: bool = False,
    candidates: List[str] | None = None,
) -> str:
    now = time.time()

    pool = candidates[:] if candidates else list(PIZZAS.keys())

    if only_wrong:
        pool_wrong = [p for p in pool if stats[p].wrong > 0]
        pool = pool_wrong or pool

    if not pool:
        pool = list(PIZZAS.keys())

    weights: List[float] = []
    for p in pool:
        stp = stats[p]
        recency_boost = min(3.0, (now - (stp.last_seen_ts or 0.0)) / 120.0)
        wrong_boost = 1.0 + (stp.wrong * 2.5)
        mastery_penalty = max(0.25, 1.0 - (stp.correct / max(1, stp.seen)))
        w = (wrong_boost * mastery_penalty) + recency_boost
        weights.append(max(0.1, w))

    return random.choices(pool, weights=weights, k=1)[0]


def build_spaced_reinforcement_sequence(
    target: str,
    pool: List[str],
    repeats: int = 5,
) -> List[str]:
    """
    Devuelve una secuencia tipo "espaciado progresivo":
    target, (0 otras), target, (1 otra), target, (2 otras), ... hasta repeats.
    """
    others = [p for p in pool if p != target]
    seq: List[str] = []

    for i in range(repeats):
        seq.append(target)

        gap = i  # 0,1,2,3,4 -> espaciado progresivo
        for _ in range(gap):
            if not others:
                break
            seq.append(random.choice(others))

    return seq


# =========================
# UI
# =========================
st.set_page_config(page_title="Trainer de Pizzas", page_icon="🍕", layout="wide")
st.title("🍕 Trainer de Pizzas (comandas → ingredientes)")


# -------- Session State init --------
if "stats" not in st.session_state:
    st.session_state.stats = default_stats()
if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "total" not in st.session_state:
    st.session_state.total = 0

# modos
if "practice_mode" not in st.session_state:
    st.session_state.practice_mode = "Todas"
if "selected_pizzas" not in st.session_state:
    st.session_state.selected_pizzas = []  # set manual (arranca vacío)

# cola de refuerzo (solo se usa en modo Difícil)
if "review_queue" not in st.session_state:
    st.session_state.review_queue = []  # lista de pizzas por mostrar pronto


def current_candidates() -> List[str] | None:
    if st.session_state.practice_mode == "Selección manual":
        return st.session_state.selected_pizzas or list(PIZZAS.keys())
    if st.session_state.practice_mode == "Difícil":
        return DIFFICULT_PIZZAS or list(PIZZAS.keys())
    return None


def current_only_wrong() -> bool:
    return st.session_state.practice_mode == "Reforzar falladas"


def pick_next_with_queue() -> str:
    """
    Si estamos en modo Difícil y hay cola de refuerzo, sale de ahí.
    Si no, usa el picker normal con candidates/only_wrong según modo.
    """
    if st.session_state.practice_mode == "Difícil" and st.session_state.review_queue:
        # Asegurar que lo que salga esté dentro del pool difícil (por seguridad)
        pool = current_candidates() or list(PIZZAS.keys())
        while st.session_state.review_queue:
            nxt = st.session_state.review_queue.pop(0)
            if nxt in pool:
                return nxt
        # si se vació por items inválidos, cae al picker normal

    return pick_next_pizza(
        st.session_state.stats,
        only_wrong=current_only_wrong(),
        candidates=current_candidates(),
    )


# current debe inicializarse DESPUÉS de helpers
if "current" not in st.session_state:
    st.session_state.current = pick_next_with_queue()

if "last_result" not in st.session_state:
    st.session_state.last_result = None  # (ok: bool, msg: str)


# -------- Sidebar config --------
with st.sidebar:
    st.header("⚙️ Configuración de práctica")

    st.session_state.practice_mode = st.radio(
        "Modo",
        ["Todas", "Reforzar falladas", "Selección manual", "Difícil"],
        index=["Todas", "Reforzar falladas", "Selección manual", "Difícil"].index(st.session_state.practice_mode),
    )

    if st.session_state.practice_mode == "Selección manual":
        st.subheader("🎯 Set de práctica")

        query = st.text_input("Buscar pizza (por nombre o número)", value="")
        options = list(PIZZAS.keys())

        if query.strip():
            q = query.strip().lower()
            filtered = [p for p in options if q in p.lower()]
        else:
            filtered = options[:10]  # para no mostrar todo de golpe

        to_add = st.selectbox(
            "Agregar una pizza",
            options=["— Elegí —"] + filtered,
            index=0
        )

        col_add, col_clear = st.columns(2)
        with col_add:
            if st.button("➕ Agregar", use_container_width=True):
                if to_add != "— Elegí —" and to_add not in st.session_state.selected_pizzas:
                    st.session_state.selected_pizzas.append(to_add)

        with col_clear:
            if st.button("🧹 Vaciar set", use_container_width=True):
                st.session_state.selected_pizzas = []

        st.divider()
        st.write("**Seleccionadas:**")

        if not st.session_state.selected_pizzas:
            st.info("No agregaste pizzas todavía. Si queda vacío, uso todas.")
        else:
            for p in st.session_state.selected_pizzas:
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.write(p)
                with c2:
                    if st.button("✖", key=f"rm_{p}"):
                        st.session_state.selected_pizzas = [x for x in st.session_state.selected_pizzas if x != p]
                        st.rerun()

    if st.session_state.practice_mode == "Difícil":
        st.subheader("🔥 Modo difícil")
        st.caption("Solo salen estas pizzas:")
        st.write(", ".join(DIFFICULT_PIZZAS) if DIFFICULT_PIZZAS else "⚠️ No hay lista difícil configurada.")
        st.divider()
        st.write("**Cola de refuerzo (próximas):**")
        if not st.session_state.review_queue:
            st.info("Vacía (se llena cuando te equivocás).")
        else:
            st.write(" → ".join(st.session_state.review_queue[:12]) + (" ..." if len(st.session_state.review_queue) > 12 else ""))
        colq1, colq2 = st.columns(2)
        with colq1:
            if st.button("🧹 Limpiar cola", use_container_width=True):
                st.session_state.review_queue = []
                st.rerun()
        with colq2:
            st.write("")

    st.divider()
    st.caption("Tip: en Difícil, si fallás una pizza, vuelve 5 veces con espaciado progresivo.")


# Si el current quedó fuera del pool del modo actual, lo re-elige
pool_now = current_candidates() or list(PIZZAS.keys())
if st.session_state.current not in pool_now:
    st.session_state.current = pick_next_with_queue()


tab_quiz, tab_repaso, tab_progreso = st.tabs(["🎯 Juego", "📚 Repaso", "💾 Progreso"])


with tab_quiz:
    colA, colB, colC, colD = st.columns(4)
    with colA:
        st.metric("Puntaje", st.session_state.score)
    with colB:
        st.metric("Racha", st.session_state.streak)
    with colC:
        acc = (st.session_state.score / st.session_state.total * 100) if st.session_state.total else 0.0
        st.metric("Precisión (%)", f"{acc:.1f}")
    with colD:
        st.caption(f"Modo: **{st.session_state.practice_mode}**")

    st.divider()

    pizza_name = st.session_state.current
    correct_set = set(PIZZAS[pizza_name])

    st.subheader(f"Comanda: **{pizza_name}**")
    st.caption("Elegí los ingredientes que lleva esa pizza (pueden ser varios).")

    picked = st.multiselect(
        "Ingredientes",
        options=INGREDIENTS_MASTER,
        default=[],
        key=f"pick_{pizza_name}_{st.session_state.total}"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.button("✅ Corregir", use_container_width=True)
    with col2:
        next_btn = st.button("➡️ Siguiente (sin corregir)", use_container_width=True)

    if next_btn:
        st.session_state.current = pick_next_with_queue()
        st.session_state.last_result = None
        st.rerun()

    if submit:
        chosen_set = set(picked)
        st.session_state.total += 1

        stp = st.session_state.stats[pizza_name]
        stp.seen += 1
        stp.last_seen_ts = time.time()

        missing = sorted(list(correct_set - chosen_set))
        extra = sorted(list(chosen_set - correct_set))

        if not missing and not extra:
            stp.correct += 1
            st.session_state.score += 1
            st.session_state.streak += 1
            st.session_state.last_result = (True, "¡Perfecto! ✅")
        else:
            stp.wrong += 1
            st.session_state.streak = 0
            msg_parts = ["Te faltó / te sobró algo ❌"]
            if missing:
                msg_parts.append(f"**Faltó:** {', '.join(missing)}")
            if extra:
                msg_parts.append(f"**Sobraba:** {', '.join(extra)}")
            msg_parts.append(f"**Correcto era:** {', '.join(sorted(list(correct_set)))}")
            st.session_state.last_result = (False, "\n\n".join(msg_parts))

            # 🔥 MODO DIFÍCIL: refuerzo espaciado progresivo (5 repeticiones)
            if st.session_state.practice_mode == "Difícil":
                pool = current_candidates() or list(PIZZAS.keys())

                # (opcional) limpiamos ocurrencias previas del mismo target para no inflar demasiado
                st.session_state.review_queue = [x for x in st.session_state.review_queue if x != pizza_name]

                seq = build_spaced_reinforcement_sequence(
                    target=pizza_name,
                    pool=pool,
                    repeats=5,
                )

                # Lo ponemos al frente para que empiece "luego del error"
                st.session_state.review_queue = seq + st.session_state.review_queue

                # límite suave para no crecer infinito
                st.session_state.review_queue = st.session_state.review_queue[:60]

        # siguiente
        st.session_state.current = pick_next_with_queue()
        st.rerun()

    if st.session_state.last_result is not None:
        ok, msg = st.session_state.last_result
        (st.success if ok else st.error)(msg)

    st.divider()

    # Lista de falladas
    wrong_rows = []
    for name, s in st.session_state.stats.items():
        if s.wrong > 0:
            wrong_rows.append((name, s.wrong, s.seen, s.correct))
    wrong_rows.sort(key=lambda x: (-x[1], -x[2]))

    st.subheader("❌ Pizzas donde te equivocaste")
    if not wrong_rows:
        st.info("Todavía no hay errores registrados.")
    else:
        df_wrong = pd.DataFrame(wrong_rows, columns=["Pizza", "Errores", "Vistas", "Aciertos"])
        st.dataframe(df_wrong, use_container_width=True, hide_index=True)


with tab_repaso:
    st.subheader("📚 Tabla completa (comanda → ingredientes)")
    rows = []
    for name, ings in PIZZAS.items():
        rows.append({"Comanda": name, "Ingredientes": ", ".join(ings)})
    df = pd.DataFrame(rows).sort_values("Comanda")
    st.dataframe(df, use_container_width=True, hide_index=True)


with tab_progreso:
    st.subheader("💾 Exportar / Importar progreso")

    colx, coly = st.columns(2)

    with colx:
        st.write("**Exportar** (descargás tu progreso en un JSON):")
        st.download_button(
            "⬇️ Descargar progreso",
            data=serialize_stats(st.session_state.stats),
            file_name="progreso_pizzas.json",
            mime="application/json",
            use_container_width=True
        )

    with coly:
        st.write("**Importar** (subís tu JSON para continuar en otro dispositivo):")
        up = st.file_uploader("Subí tu progreso_pizzas.json", type=["json"])
        if up is not None:
            try:
                text = up.read().decode("utf-8")
                st.session_state.stats = deserialize_stats(text)
                st.success("Progreso importado ✅")
            except Exception as e:
                st.error(f"No pude importar ese archivo: {e}")

    st.divider()

    if st.button("🧹 Resetear progreso", use_container_width=True):
        st.session_state.stats = default_stats()
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.total = 0
        st.session_state.review_queue = []
        st.session_state.current = pick_next_with_queue()
        st.session_state.last_result = None
        st.success("Listo: progreso reseteado.")
