import io
import json
import math
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# AMBER V0.1 — NANOMAX-STYLE FRONTEND PROTOTYPE
# Research software prototype only.
# No clinically derived coefficients or performance claims.
# ============================================================

st.set_page_config(
    page_title="AMBER V0.1",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "AMBER V0.1"
APP_STATUS = "NANOMAX-STYLE FRONTEND PROTOTYPE"
MODEL_STATUS = "DEMONSTRATION ONLY"
ASSAY_STATUS = "PROTOTYPE SPECIFICATION"

# Prototype interface ranges only — NOT experimentally locked reportable ranges.
AB40_RANGE = (20.0, 2000.0)
AB42_RANGE = (2.0, 200.0)

# DEMONSTRATION COEFFICIENTS ONLY — NOT CLINICALLY DERIVED.
DEMO_B = {"intercept": -1.40, "R": -1.00, "M": 0.18}
DEMO_C = {"intercept": -1.70, "R": -1.10, "M": 0.20, "age": 0.012, "sex": 0.15}

MODEL_REGISTRY = pd.DataFrame([
    {
        "Model ID": "AMBER-DEMO-B",
        "Configuration": "AMBER-B",
        "Inputs": "Aβ40, Aβ42",
        "Status": "Demo only",
        "Purpose": "Frontend / workflow testing",
    },
    {
        "Model ID": "AMBER-DEMO-C",
        "Configuration": "AMBER-C",
        "Inputs": "Aβ40, Aβ42, age, sex",
        "Status": "Demo only",
        "Purpose": "Frontend / workflow testing",
    },
    {
        "Model ID": "AMBER-B-V1.0",
        "Configuration": "AMBER-B",
        "Inputs": "R, M",
        "Status": "Future locked model",
        "Purpose": "Clinical research inference after validation",
    },
    {
        "Model ID": "AMBER-C-V1.0",
        "Configuration": "AMBER-C",
        "Inputs": "R, M, age, sex",
        "Status": "Future locked model",
        "Purpose": "Clinical extension if incremental value is validated",
    },
])

ASSAY_REGISTRY = pd.DataFrame([
    {
        "Assay ID": "DNA-COMPASS-PROTOTYPE",
        "Assay": "DNA Compass",
        "Version": "Prototype specification",
        "Status": "Under development",
        "Units": "pg/mL",
        "Aβ40 range": "UI placeholder only",
        "Aβ42 range": "UI placeholder only",
    },
    {
        "Assay ID": "DNA-COMPASS-V1",
        "Assay": "DNA Compass",
        "Version": "Future locked version",
        "Status": "Not yet analytically locked",
        "Units": "To be locked",
        "Aβ40 range": "To be established",
        "Aβ42 range": "To be established",
    },
])

st.markdown("""
<style>
:root{
 --bg:#07111F;--panel:#0B1728;--panel2:#0F2034;--line:#1D344D;
 --cyan:#18D3F2;--cyan2:#58E4F7;--gold:#F7C948;--text:#F4F8FC;
 --muted:#A9B6C7;--danger:#FF6B6B;--ok:#55D98A;--warn:#F3C969;
}
.block-container{max-width:1450px;padding-top:3.6rem !important;padding-bottom:2.2rem}
.stApp{background:radial-gradient(circle at 78% 8%,rgba(24,211,242,.08),transparent 26%),linear-gradient(180deg,#07111F 0%,#081523 100%);color:var(--text)}
header[data-testid="stHeader"]{background:rgba(7,17,31,.96);border-bottom:1px solid rgba(255,255,255,.04)}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#06101D,#091625);border-right:1px solid #14263B}
section[data-testid="stSidebar"] > div{padding-top:.8rem}
[data-testid="stSidebarNav"]{display:none}

.amber-side-logo{width:108px;height:108px;border-radius:50%;border:2px solid var(--cyan);margin:.25rem auto .7rem;display:flex;align-items:center;justify-content:center;position:relative;color:var(--cyan);font-weight:900;font-size:1.6rem;box-shadow:0 0 28px rgba(24,211,242,.16),inset 0 0 18px rgba(24,211,242,.06)}
.amber-side-logo:before,.amber-side-logo:after{content:"";position:absolute;border:1px solid rgba(24,211,242,.32);border-radius:50%}
.amber-side-logo:before{width:84px;height:84px}.amber-side-logo:after{width:64px;height:64px}
.side-title{text-align:center;font-size:1.26rem;font-weight:850;color:#fff}.side-title span{color:var(--gold)}
.side-sub{text-align:center;color:#91A2B5;font-size:.76rem;line-height:1.45;margin:.32rem 0 1rem}
section[data-testid="stSidebar"] div[role="radiogroup"]{gap:.28rem}
section[data-testid="stSidebar"] div[role="radiogroup"] label{background:#0B1728;border:1px solid #162B42;padding:.5rem .62rem;border-radius:9px;color:#D7E1EC}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{border-color:#1B5D71;background:#0D2033}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){background:linear-gradient(90deg,rgba(24,211,242,.15),rgba(88,228,247,.04));border-color:#1DCBE8;color:#fff;box-shadow:inset 3px 0 0 #18D3F2}
section[data-testid="stSidebar"] div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-weight:700;font-size:.88rem;color:#E6EEF6}
.credit-card{margin-top:1.1rem;border:1px solid #17304B;border-radius:14px;padding:13px;background:linear-gradient(180deg,#0C1A2C,#091523);color:#D8E2EE;font-size:.76rem;line-height:1.45}
.credit-card .label{color:#8294A8;font-size:.66rem;text-transform:uppercase;letter-spacing:.05em}.credit-card .name{font-weight:800;color:#fff;margin-bottom:.48rem}.credit-card .accent{color:var(--cyan2)}

.top{display:none}
.kicker{color:var(--cyan2);font-size:.72rem;font-weight:850;text-transform:uppercase;letter-spacing:.08em}
.title{color:#fff;font-size:1.72rem;font-weight:850;margin:.22rem 0 .9rem}
.hero{border:1px solid #14384B;border-radius:20px;padding:29px 31px;background:linear-gradient(115deg,rgba(12,36,53,.97),rgba(8,25,40,.98));box-shadow:0 14px 36px rgba(0,0,0,.20)}
.hero h1{color:#fff;font-size:2.35rem;line-height:1.14;letter-spacing:-.035em;margin:.15rem 0 .8rem}.hero p{color:#C1CDDA;line-height:1.65;font-size:1rem}
.card{border:1px solid #17314A;border-radius:16px;padding:17px 18px;background:linear-gradient(180deg,#0D1B2E,#0A1726);height:100%;box-shadow:0 7px 20px rgba(0,0,0,.10)}
.icon{width:39px;height:39px;border-radius:11px;background:#0C2734;display:flex;align-items:center;justify-content:center;color:var(--cyan2);border:1px solid #1D5263;font-size:1rem;margin-bottom:.7rem;font-weight:850}
.cardtitle{color:#fff;font-weight:850;font-size:1rem;margin-bottom:.3rem}.cardbody{color:#AEBBCC;line-height:1.52;font-size:.9rem}
.metricbox{border:1px solid #17314A;border-radius:14px;background:#0A1828;padding:13px;text-align:center}.metricname{color:#8295A9;font-size:.72rem;font-weight:750}.metricvalue{color:#fff;font-size:1.48rem;font-weight:850;margin-top:.15rem}
.notice{border:1px solid #5E4C1E;background:#1C190E;color:#E8D795;border-radius:13px;padding:13px 15px}.info{border-left:3px solid var(--cyan);background:#0B1C2B;color:#C8D5E3;border-radius:0 12px 12px 0;padding:13px 15px}.danger{border:1px solid #653333;background:#2A1518;color:#FFC0C0;border-radius:13px;padding:13px 15px}.success{border:1px solid #1D5A38;background:#0E261B;color:#B9ECCC;border-radius:13px;padding:13px 15px}
.placeholder{border:1px dashed #28506B;border-radius:16px;min-height:180px;display:flex;align-items:center;justify-content:center;text-align:center;background:#091827;color:#9BAABC;padding:20px}.eqpanel{border:1px solid #17314A;border-radius:15px;background:#091827;padding:14px 16px}.footer{border-top:1px solid #17314A;margin-top:24px;padding-top:12px;color:#718398;font-size:.75rem;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.qcpass{font-weight:800;color:#55D98A}.qcfail{font-weight:800;color:#FF6B6B}.small{font-size:.79rem;color:#8697AA}

h1,h2,h3,h4{color:#fff !important}p,li,label{color:#C6D1DE}small{color:#8797AA !important}
div[data-testid="stTextInput"] input,div[data-testid="stNumberInput"] input,div[data-testid="stTextArea"] textarea,div[data-baseweb="select"]>div{background:#0D1929 !important;color:white !important;border-color:#20384F !important}
.stButton>button{background:linear-gradient(90deg,#16B9D5,#6959FF);color:#fff;border:none;border-radius:10px;font-weight:800}.stDownloadButton>button{background:#0D2133;color:#D8E5EF;border:1px solid #23445F;border-radius:10px;font-weight:700}
[data-testid="stDataFrame"]{border:1px solid #17314A;border-radius:12px}
[data-testid="stPlotlyChart"]{border-radius:16px;overflow:hidden}
</style>
""", unsafe_allow_html=True)

def card(icon, title, body):
    return f'<div class="card"><div class="icon">{icon}</div><div class="cardtitle">{title}</div><div class="cardbody">{body}</div></div>'

def derive(ab40, ab42):
    if ab40 <= 0 or ab42 <= 0:
        raise ValueError("Aβ40 and Aβ42 must both be greater than zero.")
    ratio = ab42 / ab40
    R = math.log10(ratio)
    M = math.log10(math.sqrt(ab40 * ab42))
    return ratio, R, M

def sigmoid(x):
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)

def demo_predict(model_name, ab40, ab42, age, sex):
    ratio, R, M = derive(ab40, ab42)
    if model_name.startswith("AMBER-B"):
        c = DEMO_B
        I = c["intercept"] + c["R"]*R + c["M"]*M
    else:
        c = DEMO_C
        sex_code = 1 if sex == "Female" else 0
        I = c["intercept"] + c["R"]*R + c["M"]*M + c["age"]*age + c["sex"]*sex_code
    p = sigmoid(I)
    return ratio, R, M, I, p*100

def run_qc(ab40, ab42, assay_id):
    results = []
    results.append(("Assay selected", bool(assay_id), assay_id or "Missing"))
    results.append(("Aβ40 is positive", ab40 > 0, f"{ab40:.2f} pg/mL"))
    results.append(("Aβ42 is positive", ab42 > 0, f"{ab42:.2f} pg/mL"))
    results.append((
        "Aβ40 within prototype UI range",
        AB40_RANGE[0] <= ab40 <= AB40_RANGE[1],
        f"{AB40_RANGE[0]:g}–{AB40_RANGE[1]:g} pg/mL (placeholder)"
    ))
    results.append((
        "Aβ42 within prototype UI range",
        AB42_RANGE[0] <= ab42 <= AB42_RANGE[1],
        f"{AB42_RANGE[0]:g}–{AB42_RANGE[1]:g} pg/mL (placeholder)"
    ))
    return results

def qc_dataframe(results):
    return pd.DataFrame([
        {
            "QC item": name,
            "Status": "PASS" if passed else "CHECK",
            "Detail": detail
        }
        for name, passed, detail in results
    ])

# Session state for a de-identified research case
defaults = {
    "sample_id": "AMB-DEMO-001",
    "case_note": "",
    "ab40": 285.0,
    "ab42": 18.5,
    "age": 68,
    "sex": "Female",
    "assay_id": "DNA-COMPASS-PROTOTYPE",
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

with st.sidebar:
    st.markdown("""
    <div class="amber-side-logo">Aβ</div>
    <div class="side-title"><span>AMBER</span> Platform</div>
    <div class="side-sub">Amyloid blood evaluation<br>and research interface</div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "Home",
            "Research Case",
            "AMBER Calculator",
            "DNA Compass / Method",
            "Model & Validation",
            "Longitudinal Demo",
            "Registries",
            "About AMBER",
        ],
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="credit-card">
      <div class="label">A Project by</div>
      <div class="name">Fahim ElKassim</div>
      <div class="label">Supervised by</div>
      <div class="name">Prof. Xingyi Ma<br><span class="accent">NanoMax Group, HIT Shenzhen</span></div>
      <div class="label">Designed and Developed by</div>
      <div class="name">Doctor Sukhera（学睿）</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HOME
# ============================================================
if page == "Home":
    st.markdown('<div class="kicker">Molecular measurement → biological interpretation</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h1>From blood biomarkers to probability<br>of cerebral amyloid positivity</h1>
      <p>
        AMBER is being developed as an integrated research platform that connects
        dual-biomarker molecular acquisition, assay quality control, transparent biomarker
        transformation, future locked probabilistic inference, report generation, and longitudinal research workflows.
        This V0.1 is a complete frontend prototype; clinical validation is intentionally deferred until real hospital data are available.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    a,b,c,d = st.columns(4, gap="large")
    with a: st.markdown(card("01","Research case","Create a de-identified sample/case and preserve assay/model context."), unsafe_allow_html=True)
    with b: st.markdown(card("02","Assay + QC","Check required inputs, positivity, units, and prototype interface ranges."), unsafe_allow_html=True)
    with c: st.markdown(card("03","AMBER inference","Use AMBER-B or AMBER-C architecture; real coefficients will be loaded later."), unsafe_allow_html=True)
    with d: st.markdown(card("04","Report + follow-up","Generate structured research output and support future repeated-measure analysis."), unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="title">System workflow</div>', unsafe_allow_html=True)
    cols = st.columns(7)
    steps = [
        ("1","Case","De-identified ID"),
        ("2","Assay","DNA Compass"),
        ("3","QC","Input checks"),
        ("4","Measure","Aβ40 + Aβ42"),
        ("5","Transform","Ratio, R, M"),
        ("6","Model","AMBER-B / C"),
        ("7","Output","Report / follow-up"),
    ]
    for col,(n,h,t) in zip(cols,steps):
        with col:
            st.markdown(f'<div class="card"><div class="cardtitle">{n}. {h}</div><div class="cardbody">{t}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>Prototype status:</b> no clinically derived coefficients, calibration, operating thresholds, ROC curves, or external-validation metrics are claimed in V0.1.</div>', unsafe_allow_html=True)

# ============================================================
# RESEARCH CASE
# ============================================================
elif page == "Research Case":
    st.markdown('<div class="kicker">Sample workflow</div><div class="title">Research Case / Sample</div>', unsafe_allow_html=True)

    st.markdown('<div class="info"><b>Privacy design:</b> use de-identified research/sample IDs only. Do not enter names, medical-record numbers, addresses, or other direct identifiers.</div>', unsafe_allow_html=True)
    st.write("")

    left,right = st.columns([1.1,1], gap="large")
    with left:
        st.markdown("### Case information")
        st.session_state.sample_id = st.text_input("Sample / research case ID", value=st.session_state.sample_id)
        st.session_state.assay_id = st.selectbox("Assay ID", ASSAY_REGISTRY["Assay ID"].tolist(), index=0)
        st.session_state.case_note = st.text_area("Research note (optional, de-identified)", value=st.session_state.case_note, height=90)

        st.markdown("### Biomarker inputs")
        st.session_state.ab40 = st.number_input("Plasma Aβ40 (pg/mL)", min_value=.01, value=float(st.session_state.ab40), step=1.0, format="%.2f")
        st.session_state.ab42 = st.number_input("Plasma Aβ42 (pg/mL)", min_value=.01, value=float(st.session_state.ab42), step=.1, format="%.2f")

        st.markdown("### Clinical variables for AMBER-C research comparison")
        st.session_state.age = st.number_input("Age (years)", min_value=18, max_value=100, value=int(st.session_state.age))
        st.session_state.sex = st.radio("Sex", ["Male","Female"], horizontal=True, index=1 if st.session_state.sex=="Female" else 0)

    with right:
        st.markdown("### Prototype assay QC")
        qc = run_qc(st.session_state.ab40, st.session_state.ab42, st.session_state.assay_id)
        qcdf = qc_dataframe(qc)
        st.dataframe(qcdf, hide_index=True, use_container_width=True)

        all_pass = all(x[1] for x in qc)
        if all_pass:
            st.markdown('<div class="success"><b>Prototype QC status: PASS</b><br>All current interface checks passed. This does not represent final analytical assay validation.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger"><b>Prototype QC status: CHECK REQUIRED</b><br>Review flagged fields before proceeding.</div>', unsafe_allow_html=True)

        st.write("")
        try:
            ratio,R,M = derive(st.session_state.ab40, st.session_state.ab42)
            c1,c2,c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metricbox"><div class="metricname">Aβ42/Aβ40</div><div class="metricvalue">{ratio:.4f}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metricbox"><div class="metricname">R</div><div class="metricvalue">{R:.3f}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metricbox"><div class="metricname">M</div><div class="metricvalue">{M:.3f}</div></div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(str(e))

        st.write("")
        st.caption("These transformations are mathematical and can be computed now. Clinical probability cannot be validated until the final model is derived.")

# ============================================================
# CALCULATOR
# ============================================================
elif page == "AMBER Calculator":
    st.markdown('<div class="kicker">Inference workflow</div><div class="title">AMBER Calculator</div>', unsafe_allow_html=True)

    current = st.session_state
    st.markdown(f'<div class="info"><b>Active research case:</b> {current.sample_id} · Assay: {current.assay_id}</div>', unsafe_allow_html=True)
    st.write("")

    demo_enabled = st.toggle("Enable illustrative demo mode", value=False, help="Uses placeholder coefficients only to test the interface.")
    model_name = st.selectbox("Model configuration", ["AMBER-B (biomarker-only)","AMBER-C (biomarker + age/sex)"])

    left,center,right = st.columns([.9,1.25,1], gap="large")

    with left:
        st.markdown("### 1. Case inputs")
        st.write(f"**Aβ40:** {current.ab40:.2f} pg/mL")
        st.write(f"**Aβ42:** {current.ab42:.2f} pg/mL")
        st.write(f"**Age:** {current.age} years")
        st.write(f"**Sex:** {current.sex}")
        st.write(f"**Assay:** {current.assay_id}")

        qc = run_qc(current.ab40, current.ab42, current.assay_id)
        all_pass = all(x[1] for x in qc)
        if all_pass:
            st.markdown('<div class="success"><b>Prototype QC: PASS</b></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger"><b>Prototype QC: CHECK REQUIRED</b></div>', unsafe_allow_html=True)

        run = st.button("Calculate illustrative score", type="primary", use_container_width=True, disabled=not demo_enabled or not all_pass)

    with center:
        st.markdown("### 2. Result")
        if not demo_enabled:
            st.markdown('<div class="placeholder"><div><b>Validated AMBER model not yet loaded</b><br><br>Future state:<br>QC-passed case → locked model → calibrated probability</div></div>', unsafe_allow_html=True)
        elif run:
            ratio,R,M,I,score = demo_predict(model_name,current.ab40,current.ab42,current.age,current.sex)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={"suffix":"/100","font":{"size":52,"color":"#071D49"}},
                title={"text":"Illustrative software output"},
                gauge={"axis":{"range":[0,100]},"bar":{"color":"#0A2F69","thickness":.22},"steps":[{"range":[0,100],"color":"#EEF3FA"}]}
            ))
            fig.update_layout(height=330,margin=dict(l=25,r=25,t=45,b=5),paper_bgcolor="#07111F",font_color="#DCE6F0")
            st.plotly_chart(fig,use_container_width=True)
            st.markdown('<div class="danger"><b>NOT A CLINICALLY DERIVED AMBER SCORE.</b><br>Placeholder coefficients are used only to test the workflow.</div>', unsafe_allow_html=True)

            st.write("")
            m1,m2,m3 = st.columns(3)
            with m1: st.markdown(f'<div class="metricbox"><div class="metricname">Aβ42/Aβ40</div><div class="metricvalue">{ratio:.4f}</div></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metricbox"><div class="metricname">R</div><div class="metricvalue">{R:.3f}</div></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metricbox"><div class="metricname">M</div><div class="metricvalue">{M:.3f}</div></div>', unsafe_allow_html=True)

            report = {
                "application": APP_VERSION,
                "status": MODEL_STATUS,
                "generated_at": datetime.now().isoformat(timespec="minutes"),
                "sample_id": current.sample_id,
                "assay_id": current.assay_id,
                "model_configuration": model_name,
                "inputs": {
                    "ab40_pg_ml": current.ab40,
                    "ab42_pg_ml": current.ab42,
                    "age": None if model_name.startswith("AMBER-B") else current.age,
                    "sex": None if model_name.startswith("AMBER-B") else current.sex,
                },
                "derived_features": {"ratio": ratio, "R": R, "M": M},
                "illustrative_score": score,
                "warning": "Placeholder coefficients only; not clinically validated."
            }

            st.download_button(
                "Download structured prototype report (.json)",
                data=json.dumps(report, indent=2),
                file_name=f"{current.sample_id}_AMBER_V01_demo_report.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.markdown('<div class="placeholder"><div><b>Demo mode enabled</b><br><br>Select Calculate illustrative score.</div></div>', unsafe_allow_html=True)

    with right:
        st.markdown("### 3. Scientific transparency")
        st.markdown('<div class="eqpanel">', unsafe_allow_html=True)
        st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
        st.markdown("**AMBER-B**")
        st.latex(r"I_B=\beta_0+\beta_RR+\beta_MM")
        st.markdown("**AMBER-C**")
        st.latex(r"I_C=\beta_0+\beta_RR+\beta_MM+\beta_A Age+\beta_S Sex")
        st.latex(r"P=\frac{1}{1+e^{-I}}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="notice"><b>Future model loading:</b> the final locked JSON model will replace demonstration coefficients after hospital-data derivation and external validation.</div>', unsafe_allow_html=True)

# ============================================================
# METHOD
# ============================================================
elif page == "DNA Compass / Method":
    st.markdown('<div class="kicker">Molecular acquisition architecture</div><div class="title">DNA Compass / Method</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
      <h1 style="font-size:2rem;">DNA Compass–enabled dual-biomarker measurement</h1>
      <p>
        The intended AMBER architecture couples quantitative acquisition of plasma Aβ40 and Aβ42
        to transparent computational interpretation of cerebral amyloid positivity.
        The public prototype deliberately omits unpublished implementation details.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    cols = st.columns(7)
    method = [
        ("01","Sample","Plasma"),
        ("02","Assay","DNA Compass"),
        ("03","Recognition","Aβ42 + Aβ40"),
        ("04","Readout","Quantitative signal"),
        ("05","QC","Assay/input checks"),
        ("06","Transform","Ratio, R, M"),
        ("07","AMBER","Probability inference"),
    ]
    for col,(ic,h,t) in zip(cols,method):
        with col: st.markdown(card(ic,h,t), unsafe_allow_html=True)

    st.write("")
    l,r = st.columns(2,gap="large")
    with l:
        st.markdown("### Biomarker transformations")
        st.latex(r"\mathrm{Ratio}=\frac{A\beta42}{A\beta40}")
        st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
        st.caption("These transformations are computed internally from measured concentrations.")

    with r:
        st.markdown("### Scientific positioning")
        st.write(
            "AMBER tests whether simultaneous quantitative information from both amyloid peptides "
            "can be translated into a calibrated estimate of cerebral amyloid pathology, and whether "
            "retaining both measurements adds reproducible information beyond the ratio alone."
        )
        st.markdown('<div class="info"><b>p-tau217:</b> treated as a contemporary comparator where available, not as something AMBER must claim to replace.</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>Public-disclosure boundary:</b> exact DNA sequences, geometry, fabrication parameters, recognition chemistry, and unpublished assay implementation details are intentionally excluded here.</div>', unsafe_allow_html=True)

# ============================================================
# MODEL & VALIDATION
# ============================================================
elif page == "Model & Validation":
    st.markdown('<div class="kicker">Evidence layer</div><div class="title">Model & Validation</div>', unsafe_allow_html=True)
    st.markdown('<div class="notice"><b>No AMBER performance metrics are claimed in V0.1.</b> This page is reserved for future real-data validation outputs.</div>', unsafe_allow_html=True)

    st.write("")
    p1,p2,p3 = st.columns(3,gap="large")
    with p1: st.markdown('<div class="placeholder"><div><b>ROC / discrimination</b><br>Awaiting outcome-labelled hospital data</div></div>', unsafe_allow_html=True)
    with p2: st.markdown('<div class="placeholder"><div><b>Calibration</b><br>Awaiting model derivation and validation</div></div>', unsafe_allow_html=True)
    with p3: st.markdown('<div class="placeholder"><div><b>Decision-curve analysis</b><br>Awaiting locked clinical operating thresholds</div></div>', unsafe_allow_html=True)

    st.write("")
    comparator_df = pd.DataFrame([
        ["Aβ40 alone","Planned","Single-biomarker comparator"],
        ["Aβ42 alone","Planned","Single-biomarker comparator"],
        ["Aβ42/Aβ40 ratio","Planned","Conventional ratio comparator"],
        ["AMBER-B","Planned","Primary biomarker-only model"],
        ["AMBER-C","Planned","Age/sex extension"],
        ["p-tau217","Optional","Contemporary comparator if available"],
        ["p-tau217/Aβ42","Optional","Contemporary ratio comparator if available"],
    ], columns=["Model / biomarker","Status","Purpose"])
    st.dataframe(comparator_df, hide_index=True, use_container_width=True)

    st.write("")
    a,b,c = st.columns(3,gap="large")
    with a: st.markdown(card("A","Discrimination","AUROC with confidence intervals, sensitivity, specificity, PPV, and NPV at locked thresholds."), unsafe_allow_html=True)
    with b: st.markdown(card("B","Calibration","Calibration intercept/slope, calibration plot, and Brier score."), unsafe_allow_html=True)
    with c: st.markdown(card("C","Clinical utility","Decision-curve analysis and prespecified rule-out / rule-in operating strategies."), unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="info"><b>Model-lock principle:</b> preprocessing, coefficients, calibration, and thresholds must be frozen before independent external validation.</div>', unsafe_allow_html=True)

# ============================================================
# LONGITUDINAL DEMO
# ============================================================
elif page == "Longitudinal Demo":
    st.markdown('<div class="kicker">Repeated-measure workflow</div><div class="title">Longitudinal Demonstration</div>', unsafe_allow_html=True)

    st.markdown('<div class="info"><b>Demonstration module only.</b> It visualizes repeated biomarker measurements and derived features. It does not claim that longitudinal AMBER score change is clinically validated.</div>', unsafe_allow_html=True)

    default_visits = pd.DataFrame([
        {"Visit":"Baseline","Aβ40 (pg/mL)":285.0,"Aβ42 (pg/mL)":18.5},
        {"Visit":"Visit 2","Aβ40 (pg/mL)":280.0,"Aβ42 (pg/mL)":18.0},
        {"Visit":"Visit 3","Aβ40 (pg/mL)":275.0,"Aβ42 (pg/mL)":17.2},
    ])

    edited = st.data_editor(
        default_visits,
        num_rows="dynamic",
        use_container_width=True,
        key="longitudinal_editor"
    )

    if len(edited) > 0:
        tmp = edited.copy()
        valid = (tmp["Aβ40 (pg/mL)"] > 0) & (tmp["Aβ42 (pg/mL)"] > 0)
        if not valid.all():
            st.warning("All longitudinal Aβ40 and Aβ42 values must be > 0.")
        tmp = tmp[valid].copy()

        if len(tmp) > 0:
            tmp["Aβ42/Aβ40"] = tmp["Aβ42 (pg/mL)"] / tmp["Aβ40 (pg/mL)"]
            tmp["R"] = tmp["Aβ42/Aβ40"].apply(lambda x: math.log10(x))
            tmp["M"] = tmp.apply(lambda r: math.log10(math.sqrt(r["Aβ40 (pg/mL)"] * r["Aβ42 (pg/mL)"])), axis=1)

            left,right = st.columns(2,gap="large")

            with left:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=tmp["Visit"], y=tmp["Aβ40 (pg/mL)"], mode="lines+markers", name="Aβ40"))
                fig.add_trace(go.Scatter(x=tmp["Visit"], y=tmp["Aβ42 (pg/mL)"], mode="lines+markers", name="Aβ42"))
                fig.update_layout(title="Biomarker concentrations", height=360, margin=dict(l=30,r=15,t=45,b=30), paper_bgcolor="#07111F", plot_bgcolor="#0A1828", font_color="#DCE6F0")
                st.plotly_chart(fig, use_container_width=True)

            with right:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=tmp["Visit"], y=tmp["Aβ42/Aβ40"], mode="lines+markers", name="Aβ42/Aβ40"))
                fig2.update_layout(title="Aβ42/Aβ40 ratio trajectory", height=360, margin=dict(l=30,r=15,t=45,b=30), paper_bgcolor="#07111F", plot_bgcolor="#0A1828", font_color="#DCE6F0")
                st.plotly_chart(fig2, use_container_width=True)

            st.dataframe(tmp, hide_index=True, use_container_width=True)

            csv_bytes = tmp.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Export longitudinal demonstration data (.csv)",
                data=csv_bytes,
                file_name="AMBER_V01_longitudinal_demo.csv",
                mime="text/csv"
            )

# ============================================================
# REGISTRIES
# ============================================================
elif page == "Registries":
    st.markdown('<div class="kicker">Traceability architecture</div><div class="title">Model & Assay Registries</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
      <h1 style="font-size:2rem;">Version-aware scientific deployment</h1>
      <p>
        AMBER separates the application, assay specification, and model artifact.
        This allows future assay bridging, model updates, recalibration, and external-validation releases
        to be versioned explicitly rather than changed silently.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("### Model registry")
    st.dataframe(MODEL_REGISTRY, hide_index=True, use_container_width=True)

    st.write("")
    st.markdown("### Assay registry")
    st.dataframe(ASSAY_REGISTRY, hide_index=True, use_container_width=True)

    st.write("")
    a,b,c = st.columns(3,gap="large")
    with a: st.markdown(card("01","Model lock","A locked model keeps its preprocessing, coefficients, calibration, and thresholds immutable."), unsafe_allow_html=True)
    with b: st.markdown(card("02","Assay lock","A deployed model is tied to a defined assay version, units, and analytical specification."), unsafe_allow_html=True)
    with c: st.markdown(card("03","New version","Material assay/model changes trigger a new version and, where needed, bridging or revalidation."), unsafe_allow_html=True)

# ============================================================
# ABOUT
# ============================================================
else:
    st.markdown('<div class="kicker">Scientific information</div><div class="title">About AMBER</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
      <h1 style="font-size:2rem;">A molecular-to-pathology research architecture</h1>
      <p>
        AMBER is being developed to connect nanoscale molecular measurement with probabilistic
        assessment of cerebral amyloid pathology. V0.1 is the complete frontend prototype and
        does not contain a clinically derived AMBER equation.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    a,b,c = st.columns(3,gap="large")
    with a: st.markdown(card("01","Intended research use","Support assay development, transparent computation, model validation, report generation, and future longitudinal research."), unsafe_allow_html=True)
    with b: st.markdown(card("02","What AMBER is not","Not currently an Alzheimer's disease diagnosis, stand-alone diagnostic test, or substitute for PET, CSF testing, or clinical assessment."), unsafe_allow_html=True)
    with c: st.markdown(card("03","Current status","Frontend complete. Assay lock, clinical coefficients, calibration, thresholds, and external validation are future steps."), unsafe_allow_html=True)

    st.write("")
    st.markdown("### Development path")
    cols = st.columns(6)
    roadmap = [
        ("1","Frontend","Complete"),
        ("2","Patent","Next"),
        ("3","Hospital data","Future"),
        ("4","Validation","Colab pipeline"),
        ("5","Model lock","After evidence"),
        ("6","App update","Validated model"),
    ]
    for col,(n,h,t) in zip(cols,roadmap):
        with col:
            st.markdown(f'<div class="card"><div class="cardtitle">{n}. {h}</div><div class="cardbody">{t}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>IP / disclosure note:</b> potentially novel assay-engineering details should remain outside the public application until institutional intellectual-property review and patent filing strategy are complete.</div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer"><div><b>{APP_VERSION}</b> · {APP_STATUS}</div><div>Model: {MODEL_STATUS} · Assay: {ASSAY_STATUS}</div><div>Research use only · Not a diagnostic test</div></div>', unsafe_allow_html=True)
