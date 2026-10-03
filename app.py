import streamlit as st
import json
import math
from dataclasses import dataclass, asdict

st.set_page_config(
    page_title="ElectroLab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container{padding-top:1rem}
.component{padding:10px;border:1px solid #40506b;border-radius:10px;margin:5px 0}
.metric-box{padding:12px;border:1px solid #40506b;border-radius:10px}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# MODELO DE DADOS
# -----------------------------
COMPONENTS = {
    "Fonte AC": {
        "icon":"🔌", "terminals":["L","N"],
        "properties":{"Tensão":220.0}
    },
    "Disjuntor": {
        "icon":"🛡️", "terminals":["IN","OUT"],
        "properties":{"Fechado":True,"Corrente nominal (A)":16.0}
    },
    "Botão NA": {
        "icon":"🟢", "terminals":["1","2"],
        "properties":{"Pressionado":False}
    },
    "Botão NF": {
        "icon":"🔴", "terminals":["1","2"],
        "properties":{"Fechado":True}
    },
    "Contator": {
        "icon":"⚙️", "terminals":["A1","A2","13","14","21","22"],
        "properties":{"Bobina (V)":220.0,"Energizado":False}
    },
    "Relé térmico": {
        "icon":"🌡️", "terminals":["95","96","97","98"],
        "properties":{"Atuado":False}
    },
    "Lâmpada": {
        "icon":"💡", "terminals":["1","2"],
        "properties":{"Potência (W)":100.0}
    },
    "Motor 3~": {
        "icon":"🌀", "terminals":["U","V","W"],
        "properties":{"Potência (CV)":5.0,"Tensão (V)":380.0}
    },
    "Resistência": {
        "icon":"🔥", "terminals":["1","2"],
        "properties":{"Potência (W)":4000.0,"Tensão (V)":380.0}
    },
    "Termostato NF": {
        "icon":"🌡️", "terminals":["1","2"],
        "properties":{"Fechado":True,"Temperatura (°C)":25.0,"Setpoint (°C)":90.0}
    },
    "Interruptor": {
        "icon":"🔘", "terminals":["L","OUT"],
        "properties":{"Fechado":False}
    },
    "Terra PE": {
        "icon":"⏚", "terminals":["PE"],
        "properties":{}
    },
}

def reset():
    st.session_state.nodes = []
    st.session_state.wires = []
    st.session_state.next_id = 1
    st.session_state.selected = None
    st.session_state.message = "Circuito limpo."

if "nodes" not in st.session_state:
    reset()

def add_component(kind):
    n = {
        "id": st.session_state.next_id,
        "tipo": kind,
        "nome": COMPONENTS[kind]["icon"] + " " + kind,
        "x": 100 + (st.session_state.next_id % 5) * 150,
        "y": 100 + (st.session_state.next_id // 5) * 100,
        "props": dict(COMPONENTS[kind]["properties"])
    }
    st.session_state.nodes.append(n)
    st.session_state.next_id += 1
    st.session_state.selected = n["id"]
    st.session_state.message = f"{kind} adicionado."

def remove_selected():
    sid = st.session_state.selected
    if sid is None:
        return
    st.session_state.nodes = [n for n in st.session_state.nodes if n["id"] != sid]
    st.session_state.wires = [
        w for w in st.session_state.wires
        if w["a"][0] != sid and w["b"][0] != sid
    ]
    st.session_state.selected = None
    st.session_state.message = "Componente removido."

def closed_component(n):
    k = n["tipo"]
    p = n["props"]
    if k == "Disjuntor": return bool(p["Fechado"])
    if k == "Botão NA": return bool(p["Pressionado"])
    if k == "Botão NF": return bool(p["Fechado"])
    if k == "Interruptor": return bool(p["Fechado"])
    if k == "Termostato NF": return bool(p["Fechado"])
    if k == "Relé térmico": return not bool(p["Atuado"])
    if k == "Contator": return bool(p["Energizado"])
    return True

def simulate():
    """Simulação didática inicial.
    A versão profissional deverá usar um solver de circuito real.
    """
    source = next((n for n in st.session_state.nodes if n["tipo"] == "Fonte AC"), None)
    if not source:
        st.session_state.message = "⚠️ Adicione uma fonte AC."
        return

    energized = {source["id"]}
    changed = True
    loops = 0

    while changed and loops < 30:
        changed = False
        loops += 1

        for w in st.session_state.wires:
            a = next((n for n in st.session_state.nodes if n["id"] == w["a"][0]), None)
            b = next((n for n in st.session_state.nodes if n["id"] == w["b"][0]), None)
            if not a or not b:
                continue

            if closed_component(a) and closed_component(b):
                if a["id"] in energized and b["id"] not in energized:
                    energized.add(b["id"]); changed = True
                if b["id"] in energized and a["id"] not in energized:
                    energized.add(a["id"]); changed = True

        # Bobina do contator: se houver caminho energizado até o contator,
        # marca a bobina como energizada.
        for n in st.session_state.nodes:
            if n["tipo"] == "Contator" and n["id"] in energized:
                if not n["props"]["Energizado"]:
                    n["props"]["Energizado"] = True
                    changed = True

    cargas = [
        n for n in st.session_state.nodes
        if n["tipo"] in ("Lâmpada","Motor 3~","Resistência")
        and n["id"] in energized
    ]

    if cargas:
        st.session_state.message = (
            "🟢 CIRCUITO ENERGIZADO — " +
            ", ".join(n["nome"] for n in cargas)
        )
    else:
        st.session_state.message = (
            "🟠 Nenhuma carga chegou a ficar energizada. "
            "Procure uma interrupção no caminho."
        )

def save_json():
    data = {
        "nodes": st.session_state.nodes,
        "wires": st.session_state.wires,
        "next_id": st.session_state.next_id
    }
    return json.dumps(data, ensure_ascii=False, indent=2)

def load_json(text):
    try:
        d = json.loads(text)
        st.session_state.nodes = d.get("nodes", [])
        st.session_state.wires = d.get("wires", [])
        st.session_state.next_id = d.get("next_id", 1)
        st.session_state.selected = None
        st.session_state.message = "Projeto carregado."
    except Exception:
        st.session_state.message = "❌ Arquivo de projeto inválido."

# -----------------------------
# SIDEBAR
# -----------------------------
st.title("⚡ ElectroLab")
st.caption("Simulador elétrico — protótipo Streamlit")

with st.sidebar:
    st.header("🧰 Componentes")

    groups = {
        "Fontes": ["Fonte AC"],
        "Proteção": ["Disjuntor","Relé térmico"],
        "Comando": ["Botão NA","Botão NF","Contator","Interruptor","Termostato NF"],
        "Cargas": ["Lâmpada","Motor 3~","Resistência"],
        "Aterramento": ["Terra PE"],
    }

    for group, items in groups.items():
        st.subheader(group)
        for item in items:
            if st.button(
                f'{COMPONENTS[item]["icon"]} {item}',
                use_container_width=True,
                key="add_"+item
            ):
                add_component(item)

    st.divider()
    st.header("📐 Modelos prontos")
    template = st.selectbox(
        "Escolha",
        ["Nenhum","Partida direta","Lâmpada residencial","Resistência + termostato"]
    )

    if st.button("📥 Carregar modelo", use_container_width=True):
        reset()
        if template == "Partida direta":
            for x in ["Fonte AC","Disjuntor","Botão NF","Botão NA","Contator","Motor 3~"]:
                add_component(x)
            st.session_state.message = "Modelo de partida direta criado."
        elif template == "Lâmpada residencial":
            for x in ["Fonte AC","Disjuntor","Interruptor","Lâmpada"]:
                add_component(x)
            st.session_state.message = "Modelo residencial criado."
        elif template == "Resistência + termostato":
            for x in ["Fonte AC","Disjuntor","Termostato NF","Resistência","Lâmpada"]:
                add_component(x)
            st.session_state.message = "Modelo de resistência criado."

    if st.button("🧹 Novo circuito", use_container_width=True):
        reset()

# -----------------------------
# ÁREA PRINCIPAL
# -----------------------------
left, center, right = st.columns([1.15, 2.5, 1.15])

with left:
    st.subheader("📋 Componentes")

    if not st.session_state.nodes:
        st.info("Adicione componentes pela lateral.")
    else:
        for n in st.session_state.nodes:
            selected = st.session_state.selected == n["id"]
            if st.button(
                ("👉 " if selected else "") + n["nome"],
                use_container_width=True,
                key=f"sel_{n['id']}"
            ):
                st.session_state.selected = n["id"]
                st.rerun()

with center:
    st.subheader("🧩 Projeto")

    st.info(
        "Esta primeira versão usa a interface do Streamlit. "
        "Na próxima etapa entraremos com editor gráfico de arrastar, "
        "bornes clicáveis e fios desenhados sobre uma área de trabalho."
    )

    if st.session_state.nodes:
        cols = st.columns(2)
        for i, n in enumerate(st.session_state.nodes):
            with cols[i % 2]:
                estado = ""
                if n["tipo"] in ["Disjuntor","Botão NF","Interruptor","Termostato NF"]:
                    estado = "🟢 fechado" if closed_component(n) else "🔴 aberto"
                elif n["tipo"] == "Botão NA":
                    estado = "🟢 pressionado" if closed_component(n) else "⚪ aberto"
                elif n["tipo"] == "Contator":
                    estado = "🟢 energizado" if n["props"]["Energizado"] else "⚪ desenergizado"

                st.markdown(
                    f'<div class="component"><b>{n["nome"]}</b><br>'
                    f'<small>Bornes: {", ".join(COMPONENTS[n["tipo"]]["terminals"])}</small><br>'
                    f'<small>{estado}</small></div>',
                    unsafe_allow_html=True
                )

    st.subheader("🔗 Ligações")
    if not st.session_state.wires:
        st.caption("Nenhuma ligação. Use a área de ligações abaixo.")
    else:
        for i, w in enumerate(st.session_state.wires):
            an = next((n for n in st.session_state.nodes if n["id"] == w["a"][0]), None)
            bn = next((n for n in st.session_state.nodes if n["id"] == w["b"][0]), None)
            if an and bn:
                st.write(f'{an["nome"]} [{w["a"][1]}]  ───  {bn["nome"]} [{w["b"][1]}]')

with right:
    st.subheader("⚙️ Propriedades")
    n = next((x for x in st.session_state.nodes if x["id"] == st.session_state.selected), None)

    if not n:
        st.caption("Selecione um componente.")
    else:
        st.write(n["nome"])
        st.caption(f'Tipo: {n["tipo"]}')

        for key, value in list(n["props"].items()):
            if isinstance(value, bool):
                n["props"][key] = st.checkbox(key, value=value, key=f"prop_{n['id']}_{key}")
            elif isinstance(value, (int,float)):
                n["props"][key] = st.number_input(
                    key, value=float(value), key=f"prop_{n['id']}_{key}"
                )
            else:
                n["props"][key] = st.text_input(
                    key, value=str(value), key=f"prop_{n['id']}_{key}"
                )

        if st.button("🗑️ Excluir", use_container_width=True):
            remove_selected()
            st.rerun()

st.divider()

# -----------------------------
# LIGAÇÕES MANUAIS
# -----------------------------
st.subheader("🔌 Criar ligação")

if len(st.session_state.nodes) >= 2:
    n1 = st.selectbox(
        "Componente A",
        st.session_state.nodes,
        format_func=lambda n: n["nome"],
        key="wire_n1"
    )
    t1 = st.selectbox(
        "Borne A",
        COMPONENTS[n1["tipo"]]["terminals"],
        key="wire_t1"
    )

    n2 = st.selectbox(
        "Componente B",
        st.session_state.nodes,
        format_func=lambda n: n["nome"],
        key="wire_n2"
    )
    t2 = st.selectbox(
        "Borne B",
        COMPONENTS[n2["tipo"]]["terminals"],
        key="wire_t2"
    )

    if st.button("➕ Criar ligação"):
        if n1["id"] != n2["id"]:
            st.session_state.wires.append({
                "a": [n1["id"],t1],
                "b": [n2["id"],t2],
                "live": False
            })
            st.session_state.message = "Ligação criada."
            st.rerun()

# -----------------------------
# SIMULAÇÃO
# -----------------------------
st.divider()
c1,c2,c3,c4 = st.columns(4)

with c1:
    if st.button("▶ SIMULAR", use_container_width=True):
        simulate()
        st.rerun()

with c2:
    if st.button("⏹ DESENERGIZAR", use_container_width=True):
        for n in st.session_state.nodes:
            if n["tipo"] == "Contator":
                n["props"]["Energizado"] = False
        st.session_state.message = "Circuito desenergizado."
        st.rerun()

with c3:
    st.download_button(
        "💾 Salvar projeto",
        data=save_json(),
        file_name="electrolab_projeto.json",
        mime="application/json",
        use_container_width=True
    )

with c4:
    uploaded = st.file_uploader(
        "📂 Abrir projeto",
        type=["json"],
        label_visibility="collapsed"
    )
    if uploaded:
        load_json(uploaded.read().decode("utf-8"))
        st.rerun()

st.success(st.session_state.message)

# -----------------------------
# MEDIÇÃO INICIAL
# -----------------------------
st.divider()
st.subheader("📟 Multímetro virtual — base")

m1,m2,m3 = st.columns(3)
with m1:
    modo = st.selectbox("Grandeza", ["Tensão AC (V)","Corrente (A)","Resistência (Ω)","Continuidade"])
with m2:
    ponto_a = st.selectbox(
        "Ponto A",
        ["—"] + [
            f'{n["nome"]} / {t}'
            for n in st.session_state.nodes
            for t in COMPONENTS[n["tipo"]]["terminals"]
        ]
    )
with m3:
    ponto_b = st.selectbox(
        "Ponto B",
        ["—"] + [
            f'{n["nome"]} / {t}'
            for n in st.session_state.nodes
            for t in COMPONENTS[n["tipo"]]["terminals"]
        ],
        key="meter_b"
    )

st.metric("Leitura", "—", help="O solver elétrico real será conectado nesta etapa do projeto.")

st.caption(
    "⚠️ A simulação atual é didática e não substitui cálculo/projeto elétrico real. "
    "O próximo núcleo será um solver de circuitos para calcular tensão, corrente, "
    "potência, impedância, curto, queda de tensão e comportamento trifásico."
)
