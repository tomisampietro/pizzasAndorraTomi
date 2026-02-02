import json
import random
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional

import pandas as pd
import streamlit as st


# =========================
# Datos
# =========================

# --- PIZZAS (ANTES DE HORNO) ---
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

# --- TOPPINGS (DESPUÉS DE HORNO) - lista prioritaria del usuario ---
POST_HORNO: Dict[str, List[str]] = {
    "0 - MARINARA": ["albahaca", "aceite de oliva"],
    "N. 1": ["parmesano", "albahaca", "aceite de oliva"],
    "N. ANCHOIS": ["albahaca"],                      # ANCHOAS
    "N. 3": ["orégano"],
    "N. SOBR": ["crema de nueces", "miel"],
    "N. 5": ["yema de huevo", "orégano"],
    "MORTA PEST": ["mortadela", "burrata", "pistachos"],
    "N. 8": ["miel", "crema de nuez"],
    "VEGAN!": ["rúcula", "aceite de oliva", "albahaca"],
    "N. 10": ["orégano"],
    "N. 12": ["parmesano", "orégano"],
    "N. 14": ["rúcula", "albahaca", "aceite de oliva"],
    "N. CURRY": ["nata", "coco rallado"],
    "PESTO XERRI": ["parmesano", "rúcula", "albahaca", "aceite de oliva"],
    "N. SPICY": ["piñones"],                          # 18 SPICY
    "N. AUB, GOR": ["crema de nueces"],
    "N. 21": ["yema de huevo"],
    "N. CECINA": ["rúcula", "miel", "orégano"],
    "N. THON": ["albahaca"],
    "N. CANILL": ["yema de huevo"],
    "SAUMON": ["rúcula"],
    "SERRANO": ["jamón serrano", "burrata", "rúcula", "aceite de oliva", "albahaca"],  # N26 / Salamandres
    "MAGRET": ["yema de huevo"],
}

# --- ENSALADAS (castellano) ---
SALADS: Dict[str, List[str]] = {
    "N*1 - ABELLETES": ["rúcula", "jamón serrano", "burrata", "tomate", "piñones", "cebolla", "albahaca"],
    "N*2 - CUBILL": ["rúcula", "cecina de León", "tomate", "miel", "nueces"],
    "N*3 - ENVALIRA": ["rúcula", "pesto", "atún", "cebolla", "tomate", "piñones"],
}

DATASETS: Dict[str, Dict[str, List[str]]] = {
    "Pizzas (antes de horno)": PIZZAS,
    "Post-horno (toppings)": POST_HORNO,
    "Ensaladas": SALADS,
}

# =========================
# Modo difícil por dataset
# =========================
DIFFICULT_BY_DATASET: Dict[str, List[str]] = {
    "Pizzas (antes de horno)": [
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
    ],
    # para post-horno y ensaladas lo dejamos vacío (si querés, armamos uno después)
    "Post-horno (toppings)": [],
    "Ensaladas": [],
}


# =========================
# Helpers
# =========================
def all_ingredients(items: Dict[str, List[str]]) -> List[str]:
    s: Set[str] = set()
    for ing_list in items.values():
        s.update(ing_list)
    return sorted(s)


# =========================
# Progreso / Stats
# =========================
@dataclass
class PizzaStats:
    seen: int = 0
    correct: int = 0
    wrong: int = 0
    last_seen_ts: float = 0.0


def default_stats_for(items: Dict[str, List[str]]) -> Dict[str, PizzaStats]:
    return {name: PizzaStats() for name in items.keys()}


def serialize_stats_store(stats_store: Dict[str, Dict[str, PizzaStats]]) -> str:
    payload = {
        dataset: {k: asdict(v) for k, v in stats.items()}
        for dataset, stats in stats_store.items()
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def deserialize_stats_store(text: str) -> Dict[str, Dict[str, PizzaStats]]:
    raw = json.loads(text)
    out: Dict[str, Dict[str, PizzaStats]] = {}
    for dataset_name, items in DATASETS.items():
        out[dataset_name] = {}
        ds_raw = raw.get(dataset_name, {})
        for name in items.keys():
            if name in ds_raw:
                out[dataset_name][name] = PizzaStats(**ds_raw[name])
            else:
                out[dataset_name][name] = PizzaStats()
    return out


def pick_next_item(
    items: Dict[str, List[str]],
    stats: Dict[str, PizzaStats],
    only_wrong: bool = False,
    candidates: Optional[List[str]] = None,
) -> str:
    now = time.time()
    pool = candidates[:] if candidates else list(items.keys())

    if only_wrong:
        pool_wrong = [p for p in pool if stats[p].wrong > 0]
        pool = pool_wrong or pool

    if not pool:
        pool = list(items.keys())

    weights: List[float] = []
    for p in pool:
        stp = stats[p]
        recency_boost = min(3.0, (now - (stp.last_seen_ts or 0.0)) / 120.0)
        wrong_boost = 1.0 + (stp.wrong * 2.5)
        mastery_penalty = max(0.25, 1.0 - (stp.correct / max(1, stp.seen)))
        w = (wrong_boost * mastery_penalty) + recency_boost
        weights.append(max(0.1, w))

    return random.choices(pool, weights=weights, k=1)[0]


def build_spaced_reinforcement_sequence(target: str, pool: List[str], repeats: int = 5) -> List[str]:
    others = [p for p in pool if p != target]
    seq: List[str] = []
    for i in range(repeats):
        seq.append(target)
        gap = i  # 0,1,2,3,4
        for _ in range(gap):
            if not others:
                break
            seq.append(random.choice(others))
    return seq


# =========================
# UI
# =========================
st.set_page_config(page_title="Trainer de Carta", page_icon="🍕", layout="wide")
st.title("🍕 Trainer de Carta (comanda → ingredientes)")

# -------- Session State init --------
if "dataset" not in st.session_state:
    st.session_state.dataset = "Pizzas (antes de horno)"

if "stats_store" not in st.session_state:
    st.session_state.stats_store = {
        name: default_stats_for(items) for name, items in DATASETS.items()
    }

if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "total" not in st.session_state:
    st.session_state.total = 0

# modos
if "practice_mode" not in st.session_state:
    st.session_state.practice_mode = "Todas"
if "selected_items" not in st.session_state:
    st.session_state.selected_items = []  # set manual

# cola de refuerzo (solo Difícil)
if "review_queue" not in st.session_state:
    st.session_state.review_queue = []


def get_active_items() -> Dict[str, List[str]]:
    return DATASETS[st.session_state.dataset]


def get_active_stats() -> Dict[str, PizzaStats]:
    return st.session_state.stats_store[st.session_state.dataset]


def current_candidates(items: Dict[str, List[str]]) -> Optional[List[str]]:
    if st.session_state.practice_mode == "Selección manual":
        return st.session_state.selected_items or list(items.keys())
    if st.session_state.practice_mode == "Difícil":
        difficult = DIFFICULT_BY_DATASET.get(st.session_state.dataset, [])
        difficult = [p for p in difficult if p in items]  # seguridad
        return difficult or list(items.keys())
    return None


def current_only_wrong() -> bool:
    return st.session_state.practice_mode == "Reforzar falladas"


def pick_next_with_queue(items: Dict[str, List[str]], stats: Dict[str, PizzaStats]) -> str:
    if st.session_state.practice_mode == "Difícil" and st.session_state.review_queue:
        pool = current_candidates(items) or list(items.keys())
        while st.session_state.review_queue:
            nxt = st.session_state.review_queue.pop(0)
            if nxt in pool:
                return nxt
    return pick_next_item(items, stats, only_wrong=current_only_wrong(), candidates=current_candidates(items))


ACTIVE_ITEMS = get_active_items()
ACTIVE_STATS = get_active_stats()
INGREDIENTS_MASTER = all_ingredients(ACTIVE_ITEMS)

# current
if "current" not in st.session_state:
    st.session_state.current = pick_next_with_queue(ACTIVE_ITEMS, ACTIVE_STATS)

if "last_result" not in st.session_state:
    st.session_state.last_result = None  # (ok: bool, msg: str)


# -------- Sidebar config --------
with st.sidebar:
    st.header("⚙️ Configuración")

    st.session_state.dataset = st.selectbox(
        "Qué practicar",
        options=list(DATASETS.keys()),
        index=list(DATASETS.keys()).index(st.session_state.dataset),
    )

    # refrescar activos tras cambiar dataset
    ACTIVE_ITEMS = get_active_items()
    ACTIVE_STATS = get_active_stats()
    INGREDIENTS_MASTER = all_ingredients(ACTIVE_ITEMS)

    st.divider()

    st.session_state.practice_mode = st.radio(
        "Modo",
        ["Todas", "Reforzar falladas", "Selección manual", "Difícil"],
        index=["Todas", "Reforzar falladas", "Selección manual", "Difícil"].index(st.session_state.practice_mode),
    )

    if st.session_state.practice_mode == "Selección manual":
        st.subheader("🎯 Set de práctica")

        query = st.text_input("Buscar (nombre / número)", value="")
        options = list(ACTIVE_ITEMS.keys())

        if query.strip():
            q = query.strip().lower()
            filtered = [p for p in options if q in p.lower()]
        else:
            filtered = options[:10]

        to_add = st.selectbox("Agregar", options=["— Elegí —"] + filtered, index=0)

        col_add, col_clear = st.columns(2)
        with col_add:
            if st.button("➕ Agregar", use_container_width=True):
                if to_add != "— Elegí —" and to_add not in st.session_state.selected_items:
                    st.session_state.selected_items.append(to_add)
        with col_clear:
            if st.button("🧹 Vaciar set", use_container_width=True):
                st.session_state.selected_items = []

        st.divider()
        st.write("**Seleccionadas:**")
        if not st.session_state.selected_items:
            st.info("Vacío → uso todas.")
        else:
            for p in st.session_state.selected_items:
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.write(p)
                with c2:
                    if st.button("✖", key=f"rm_{st.session_state.dataset}_{p}"):
                        st.session_state.selected_items = [x for x in st.session_state.selected_items if x != p]
                        st.rerun()

    if st.session_state.practice_mode == "Difícil":
        difficult = DIFFICULT_BY_DATASET.get(st.session_state.dataset, [])
        difficult = [p for p in difficult if p in ACTIVE_ITEMS]
        st.subheader("🔥 Modo difícil")
        st.caption("Solo salen estos ítems:")
        st.write(", ".join(difficult) if difficult else "⚠️ No hay lista difícil para este dataset.")
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
    st.caption("Tip: Difícil repite lo fallado 5 veces con espaciado.")


# Si current quedó fuera del pool, re-elegir
pool_now = current_candidates(ACTIVE_ITEMS) or list(ACTIVE_ITEMS.keys())
if st.session_state.current not in pool_now:
    st.session_state.current = pick_next_with_queue(ACTIVE_ITEMS, ACTIVE_STATS)


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
        st.caption(f"Dataset: **{st.session_state.dataset}** · Modo: **{st.session_state.practice_mode}**")

    st.divider()

    item_name = st.session_state.current
    correct_set = set(ACTIVE_ITEMS[item_name])

    st.subheader(f"Comanda: **{item_name}**")
    st.caption("Elegí los ingredientes correctos (pueden ser varios).")

    picked = st.multiselect(
        "Ingredientes",
        options=INGREDIENTS_MASTER,
        default=[],
        key=f"pick_{st.session_state.dataset}_{item_name}_{st.session_state.total}"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.button("✅ Corregir", use_container_width=True)
    with col2:
        next_btn = st.button("➡️ Siguiente (sin corregir)", use_container_width=True)

    if next_btn:
        st.session_state.current = pick_next_with_queue(ACTIVE_ITEMS, ACTIVE_STATS)
        st.session_state.last_result = None
        st.rerun()

    if submit:
        chosen_set = set(picked)
        st.session_state.total += 1

        stp = ACTIVE_STATS[item_name]
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

            # Refuerzo solo si Difícil
            if st.session_state.practice_mode == "Difícil":
                pool = current_candidates(ACTIVE_ITEMS) or list(ACTIVE_ITEMS.keys())
                st.session_state.review_queue = [x for x in st.session_state.review_queue if x != item_name]
                seq = build_spaced_reinforcement_sequence(target=item_name, pool=pool, repeats=5)
                st.session_state.review_queue = (seq + st.session_state.review_queue)[:60]

        st.session_state.current = pick_next_with_queue(ACTIVE_ITEMS, ACTIVE_STATS)
        st.rerun()

    if st.session_state.last_result is not None:
        ok, msg = st.session_state.last_result
        (st.success if ok else st.error)(msg)

    st.divider()

    # Lista de falladas (solo del dataset activo)
    wrong_rows = []
    for name, s in ACTIVE_STATS.items():
        if s.wrong > 0:
            wrong_rows.append((name, s.wrong, s.seen, s.correct))
    wrong_rows.sort(key=lambda x: (-x[1], -x[2]))

    st.subheader("❌ Ítems donde te equivocaste (dataset actual)")
    if not wrong_rows:
        st.info("Todavía no hay errores registrados.")
    else:
        df_wrong = pd.DataFrame(wrong_rows, columns=["Comanda", "Errores", "Vistas", "Aciertos"])
        st.dataframe(df_wrong, use_container_width=True, hide_index=True)


with tab_repaso:
    st.subheader("📚 Tabla completa (comanda → ingredientes) - dataset actual")
    rows = [{"Comanda": name, "Ingredientes": ", ".join(ings)} for name, ings in ACTIVE_ITEMS.items()]
    df = pd.DataFrame(rows).sort_values("Comanda")
    st.dataframe(df, use_container_width=True, hide_index=True)


with tab_progreso:
    st.subheader("💾 Exportar / Importar progreso (todos los datasets)")

    colx, coly = st.columns(2)

    with colx:
        st.write("**Exportar** (JSON):")
        st.download_button(
            "⬇️ Descargar progreso",
            data=serialize_stats_store(st.session_state.stats_store),
            file_name="progreso_carta.json",
            mime="application/json",
            use_container_width=True
        )

    with coly:
        st.write("**Importar** (subí tu progreso_carta.json):")
        up = st.file_uploader("Subí tu progreso_carta.json", type=["json"])
        if up is not None:
            try:
                text = up.read().decode("utf-8")
                st.session_state.stats_store = deserialize_stats_store(text)
                st.success("Progreso importado ✅")
            except Exception as e:
                st.error(f"No pude importar ese archivo: {e}")

    st.divider()

    if st.button("🧹 Resetear progreso", use_container_width=True):
        st.session_state.stats_store = {name: default_stats_for(items) for name, items in DATASETS.items()}
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.total = 0
        st.session_state.review_queue = []
        ACTIVE_ITEMS = get_active_items()
        ACTIVE_STATS = get_active_stats()
        st.session_state.current = pick_next_with_queue(ACTIVE_ITEMS, ACTIVE_STATS)
        st.session_state.last_result = None
        st.success("Listo: progreso reseteado.")
