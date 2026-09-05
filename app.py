
import base64
import json
import math
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# AMBER V0.1 — DIRECT UI FINAL
# Image-free scientific UI (institutional logo excepted)
# ============================================================

st.set_page_config(
    page_title="AMBER Score Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "AMBER V0.1"
MODEL_STATUS = "DEMONSTRATION ONLY"

# Placeholder coefficients for UI testing only.
# These are NOT clinically derived AMBER coefficients.
DEMO_B = {"intercept": -1.40, "R": -1.00, "M": 0.18}
DEMO_C = {"intercept": -1.70, "R": -1.10, "M": 0.20, "age": 0.012, "sex": 0.15}

if "amber_result" not in st.session_state:
    st.session_state.amber_result = None
if "amber_report" not in st.session_state:
    st.session_state.amber_report = None

# ----------------------------
# Logo
# ----------------------------
try:
    with open("assets/hitsz_logo.png", "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode("ascii")
except Exception:
    LOGO_B64 = ""

# ----------------------------
# Style
# ----------------------------
st.markdown("""
<style>
:root{
  --navy:#06285F;
  --navy2:#0B3D8A;
  --gold:#F4B42D;
  --blue:#1768B2;
  --cyan:#2AA8C9;
  --ink:#162741;
  --muted:#65778E;
  --line:#D8E4F0;
  --pale:#F7FAFE;
  --pale2:#EEF5FD;
  --warn:#FFF9EA;
  --danger:#FFF1F1;
  --success:#EEF9F1;
}
html, body, [class*="css"]{
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.stApp{background:#FFFFFF;color:var(--ink)}
.block-container{
  max-width:1520px;
  padding-top:3.8rem !important;
  padding-bottom:2rem;
}
header[data-testid="stHeader"]{
  background:rgba(255,255,255,.97);
  border-bottom:1px solid #EEF3F7;
}

/* Header */
.hero{
  background:linear-gradient(105deg,#031D48 0%,#06285F 60%,#0B3D8A 100%);
  color:white;
  border-radius:0 0 24px 24px;
  padding:21px 29px 24px;
  margin:-1rem 0 1rem;
  box-shadow:0 14px 30px rgba(5,40,95,.11);
}
.hero-brand{display:flex;align-items:center;gap:18px}
.hero-logo{
  width:66px;height:66px;object-fit:contain;
  filter:brightness(0) invert(1);opacity:.98
}
.hero-fallback{
  width:62px;height:62px;border:2px solid var(--gold);border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  color:var(--gold);font-weight:900;font-size:1.25rem
}
.hero-title{
  font-size:2.28rem;line-height:1;font-weight:850;letter-spacing:-.035em
}
.hero-title .amber{color:var(--gold)}
.hero-sub{color:#E8EFF8;margin-top:.42rem;font-size:.98rem}
.hero-badges{display:flex;gap:.42rem;flex-wrap:wrap;margin-top:.74rem}
.badge{
  padding:.29rem .62rem;border-radius:999px;
  background:rgba(255,255,255,.09);
  border:1px solid rgba(255,255,255,.16);
  color:white;font-size:.68rem;font-weight:760
}

/* Navigation */
div[data-testid="stSegmentedControl"]{margin-bottom:1rem}
div[data-testid="stSegmentedControl"] button{
  border-radius:9px !important;
  font-weight:750 !important;
  min-height:40px
}

/* General */
.kicker{
  color:var(--navy2);font-size:.72rem;font-weight:850;
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:.22rem
}
.page-title{color:var(--navy);font-size:1.75rem;font-weight:850;margin-bottom:.85rem}
.section-title{color:var(--navy);font-size:1.35rem;font-weight:850;margin:1.05rem 0 .65rem}
.panel{
  border:1px solid var(--line);border-radius:16px;
  padding:19px;background:#fff;height:100%;
  box-shadow:0 6px 18px rgba(27,75,118,.045)
}
.soft{
  border:1px solid #C9DBEE;border-radius:14px;
  padding:14px 16px;background:linear-gradient(180deg,#FBFDFF,#F2F7FD)
}
.info{
  border-left:3px solid var(--cyan);background:#F2F8FC;
  color:#31566C;border-radius:0 12px 12px 0;padding:12px 14px
}
.notice{
  border:1px solid #ECD8A6;background:var(--warn);
  color:#6B561B;border-radius:12px;padding:12px 14px
}
.danger{
  border:1px solid #F0C8C8;background:var(--danger);
  color:#9B3232;border-radius:12px;padding:12px 14px
}
.success{
  border:1px solid #C8E4D0;background:var(--success);
  color:#2B6840;border-radius:12px;padding:12px 14px
}
.placeholder{
  min-height:280px;border:1px dashed #AFC4DC;border-radius:16px;
  background:#FAFCFF;display:flex;align-items:center;justify-content:center;
  text-align:center;color:#6C7E93;padding:22px
}
.metric-card{
  border:1px solid var(--line);border-radius:13px;padding:12px;
  background:#fff;text-align:center
}
.metric-name{color:#77889D;font-size:.71rem;font-weight:750}
.metric-value{color:var(--navy);font-weight:850;font-size:1.46rem;margin-top:.15rem}
.eqpanel{
  border:1px solid var(--line);border-radius:15px;
  background:#FAFCFE;padding:14px 16px
}
.footer{
  border-top:1px solid var(--line);margin-top:1.4rem;padding-top:.8rem;
  color:#7D8D9E;font-size:.74rem;display:flex;justify-content:space-between;
  flex-wrap:wrap;gap:12px
}

/* Direct UI visual language */
.flow{
  display:flex;align-items:stretch;gap:10px;flex-wrap:wrap
}
.flow-card{
  flex:1 1 150px;min-width:145px;
  border:1px solid var(--line);border-radius:15px;
  background:#fff;padding:15px 14px;position:relative;
  box-shadow:0 5px 14px rgba(29,78,119,.035)
}
.flow-num{
  width:31px;height:31px;border-radius:9px;
  display:flex;align-items:center;justify-content:center;
  background:#EDF4FD;color:var(--navy2);font-weight:850;margin-bottom:.55rem
}
.flow-title{color:var(--navy);font-weight:850;margin-bottom:.28rem}
.flow-body{color:#5F7288;font-size:.86rem;line-height:1.45}
.arrow{
  align-self:center;color:var(--blue);font-size:1.35rem;font-weight:850
}
.question-grid{
  display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  gap:14px
}
.qcard{
  border:1px solid var(--line);border-radius:15px;padding:17px;background:#fff
}
.qicon{
  width:38px;height:38px;border-radius:11px;background:#EEF5FD;
  display:flex;align-items:center;justify-content:center;
  color:var(--navy2);font-weight:900;margin-bottom:.65rem
}
.qtitle{color:var(--navy);font-weight:850;margin-bottom:.3rem}
.qbody{color:#5D7186;font-size:.89rem;line-height:1.48}

/* Molecular workflow */
.mol-wrap{
  border:1px solid var(--line);border-radius:18px;background:#FBFDFF;
  padding:20px
}
.mol-flow{
  display:grid;grid-template-columns:repeat(6,1fr);gap:10px;align-items:stretch
}
.mol-step{
  border:1px solid #D3E0EC;border-radius:14px;background:#fff;
  padding:15px 12px;text-align:center
}
.mol-symbol{
  width:44px;height:44px;border-radius:50%;margin:0 auto .55rem;
  background:linear-gradient(135deg,#EAF3FE,#F9FCFF);
  border:1px solid #C9DAEB;
  display:flex;align-items:center;justify-content:center;
  color:var(--navy2);font-size:1.05rem;font-weight:850
}
.mol-title{color:var(--navy);font-weight:850;font-size:.92rem}
.mol-body{color:#6A7B8E;font-size:.79rem;line-height:1.4;margin-top:.25rem}

/* Timeline */
.timeline{
  display:grid;grid-template-columns:repeat(5,1fr);gap:12px
}
.tstep{
  border:1px solid var(--line);border-radius:15px;background:#fff;padding:16px;
  position:relative
}
.tnum{
  width:30px;height:30px;border-radius:50%;background:var(--navy);
  color:#fff;display:flex;align-items:center;justify-content:center;
  font-weight:850;margin-bottom:.55rem
}
.ttitle{color:var(--navy);font-weight:850}
.tbody{color:#65788D;font-size:.86rem;line-height:1.45;margin-top:.25rem}
.tstatus{
  display:inline-block;margin-top:.7rem;padding:.25rem .55rem;border-radius:999px;
  background:#F0F5FB;color:var(--blue);font-size:.7rem;font-weight:750
}

.stButton>button{
  background:linear-gradient(90deg,#06285F,#0B3D8A);
  color:#fff;border:none;border-radius:10px;font-weight:850;min-height:46px
}
.stDownloadButton>button{
  background:#fff;color:var(--navy);border:1px solid #BDD2E9;
  border-radius:10px;font-weight:750
}
h1,h2,h3,h4{color:var(--navy)!important}

@media (max-width: 900px){
  .question-grid{grid-template-columns:1fr}
  .mol-flow{grid-template-columns:1fr 1fr}
  .timeline{grid-template-columns:1fr 1fr}
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Helpers
# ----------------------------
def derive(ab40, ab42):
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
    return ratio, R, M, sigmoid(I) * 100

logo_html = (
    f'<img class="hero-logo" src="data:image/png;base64,{LOGO_B64}" alt="HIT Shenzhen logo">'
    if LOGO_B64 else
    '<div class="hero-fallback">Aβ</div>'
)

st.markdown(f"""
<div class="hero">
  <div class="hero-brand">
    {logo_html}
    <div>
      <div class="hero-title"><span class="amber">AMBER</span> Score Platform</div>
      <div class="hero-sub">Blood-based molecular research platform for estimation of cerebral amyloid positivity.</div>
    </div>
  </div>
  <div class="hero-badges">
    <span class="badge">V0.1 · RESEARCH PROTOTYPE</span>
    <span class="badge">DNA COMPASS + COMPUTATIONAL INFERENCE</span>
    <span class="badge">NO CLINICAL VALIDATION CLAIMS</span>
  </div>
</div>
""", unsafe_allow_html=True)

pages = ["Home", "AMBER Calculator", "DNA Compass / Method", "Model & Validation", "About AMBER"]
page = st.segmented_control("Navigation", pages, default="Home", label_visibility="collapsed") or "Home"

# ============================================================
# 1. HOME
# ============================================================
if page == "Home":
    st.markdown('<div class="kicker">Research concept</div><div class="page-title">Why AMBER, and how does it work?</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="soft">
      <b style="color:#06285F;font-size:1.05rem">Main scientific question</b><br><br>
      Can simultaneous blood-based measurement of Aβ40 and Aβ42, enabled by a programmable DNA Compass assay,
      support a transparent and eventually validated estimate of PET-defined cerebral amyloid positivity?
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Why this project matters</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="question-grid">
      <div class="qcard">
        <div class="qicon">1</div>
        <div class="qtitle">Imaging-defined pathology</div>
        <div class="qbody">Amyloid PET can define cerebral amyloid pathology, but it is not a simple blood-based measurement workflow.</div>
      </div>
      <div class="qcard">
        <div class="qicon">2</div>
        <div class="qtitle">Two related biomarkers</div>
        <div class="qbody">Aβ40 and Aβ42 are highly related peptides. Measuring both accurately in one system is an analytical and biological challenge.</div>
      </div>
      <div class="qcard">
        <div class="qicon">3</div>
        <div class="qtitle">Translation gap</div>
        <div class="qbody">A molecular measurement becomes scientifically useful only if it can be linked to a transparent, calibrated and externally validated pathology estimate.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">AMBER research pathway</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="flow">
      <div class="flow-card">
        <div class="flow-num">1</div>
        <div class="flow-title">Measure</div>
        <div class="flow-body">Quantify plasma Aβ40 and Aβ42 using the DNA Compass analytical workflow.</div>
      </div>
      <div class="arrow">→</div>
      <div class="flow-card">
        <div class="flow-num">2</div>
        <div class="flow-title">Transform</div>
        <div class="flow-body">Derive Aβ42/Aβ40 and the interpretable relative-composition (R) and abundance (M) terms.</div>
      </div>
      <div class="arrow">→</div>
      <div class="flow-card">
        <div class="flow-num">3</div>
        <div class="flow-title">Model</div>
        <div class="flow-body">Compare ratio-only, AMBER-B, and the prespecified AMBER-C extension.</div>
      </div>
      <div class="arrow">→</div>
      <div class="flow-card">
        <div class="flow-num">4</div>
        <div class="flow-title">Validate</div>
        <div class="flow-body">Use PET-linked hospital data for discrimination, calibration and clinical-utility analysis.</div>
      </div>
      <div class="arrow">→</div>
      <div class="flow-card">
        <div class="flow-num">5</div>
        <div class="flow-title">Translate</div>
        <div class="flow-body">Load only a locked, validated model into the future AMBER production interface.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="notice">
      <b>Current stage:</b> AMBER V0.1 demonstrates the scientific and software architecture only.
      Clinical coefficients, thresholds and performance claims will be added only after real PET-linked data are analyzed.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 2. CALCULATOR
# ============================================================
elif page == "AMBER Calculator":
    st.markdown('<div class="kicker">Core computational interface</div><div class="page-title">AMBER Calculator</div>', unsafe_allow_html=True)

    with st.form("amber_calculation_form"):
        left, mid, right = st.columns([1, 1.05, 1], gap="large")

        with left:
            st.markdown("### 1. Input values")
            model_name = st.selectbox(
                "Model configuration",
                ["AMBER-B (biomarker-only)", "AMBER-C (biomarker + age/sex)"]
            )
            amber_b = model_name.startswith("AMBER-B")

            if not amber_b:
                st.markdown("#### Demographics")
                age = st.number_input("Age (years)", min_value=18, max_value=100, value=68)
                sex = st.radio("Sex", ["Male", "Female"], horizontal=True, index=1)
            else:
                age = 68
                sex = "Female"

            st.markdown("#### Biomarker measurements")
            ab40 = st.number_input(
                "Plasma Aβ40 concentration (pg/mL)",
                min_value=0.01, value=285.0, step=1.0, format="%.2f"
            )
            ab42 = st.number_input(
                "Plasma Aβ42 concentration (pg/mL)",
                min_value=0.01, value=18.5, step=0.1, format="%.2f"
            )

            demo_mode = st.checkbox(
                "Use illustrative demo probability",
                value=False,
                help="Uses placeholder coefficients only to demonstrate the software pathway."
            )

            submitted = st.form_submit_button(
                "CALCULATE AMBER SCORE",
                use_container_width=True
            )

        with mid:
            st.markdown("### 2. Results")
            if not submitted:
                st.markdown("""
                <div class="placeholder">
                  <div>
                    Enter the values on the left and click<br>
                    <b style="color:#06285F">CALCULATE AMBER SCORE</b>.<br><br>
                    Nothing is calculated automatically.
                  </div>
                </div>
                """, unsafe_allow_html=True)

        with right:
            st.markdown("### 3. Scientific basis")
            st.markdown('<div class="eqpanel">', unsafe_allow_html=True)
            st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
            st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
            st.markdown("**AMBER-B**")
            st.latex(r"I_B=\beta_0+\beta_RR+\beta_MM")
            st.markdown("**AMBER-C**")
            st.latex(r"I_C=\beta_0+\beta_RR+\beta_MM+\beta_A Age+\beta_S Sex")
            st.latex(r"P=\frac{1}{1+e^{-I}}")
            st.markdown('</div>', unsafe_allow_html=True)

    # Render results OUTSIDE the form so downloads are legal.
    if submitted:
        ratio, R, M = derive(ab40, ab42)

        result = {
            "model_name": model_name,
            "ab40": ab40,
            "ab42": ab42,
            "age": None if amber_b else age,
            "sex": None if amber_b else sex,
            "ratio": ratio,
            "R": R,
            "M": M,
            "demo_mode": demo_mode,
        }

        if demo_mode:
            ratio, R, M, score = demo_predict(model_name, ab40, ab42, age, sex)
            result["score"] = score
        else:
            result["score"] = None

        st.session_state.amber_result = result

        report = {
            "application": APP_VERSION,
            "generated_at": datetime.now().isoformat(timespec="minutes"),
            "status": "DEMONSTRATION ONLY" if demo_mode else "DERIVED FEATURES ONLY",
            "configuration": model_name,
            "inputs": {
                "ab40_pg_ml": ab40,
                "ab42_pg_ml": ab42,
                "age": None if amber_b else age,
                "sex": None if amber_b else sex,
            },
            "derived": {"ratio": ratio, "R": R, "M": M},
            "illustrative_score": result["score"],
        }
        st.session_state.amber_report = report

    if st.session_state.amber_result is not None:
        r = st.session_state.amber_result
        st.markdown('<div class="section-title">Calculated output</div>', unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-name">Aβ42/Aβ40</div><div class="metric-value">{r["ratio"]:.4f}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-name">R</div><div class="metric-value">{r["R"]:.3f}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-name">M</div><div class="metric-value">{r["M"]:.3f}</div></div>', unsafe_allow_html=True)

        st.write("")
        if r["demo_mode"]:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=r["score"],
                number={"suffix":"/100", "font":{"size":58, "color":"#06285F"}},
                title={"text":"Illustrative AMBER software output"},
                gauge={
                    "axis":{"range":[0,100]},
                    "bar":{"color":"#0B3D8A","thickness":.20},
                    "bgcolor":"#F1F6FC",
                    "bordercolor":"#D7E3F1",
                }
            ))
            fig.update_layout(
                height=340,
                margin=dict(l=20,r=20,t=50,b=0),
                paper_bgcolor="white"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
            <div class="danger">
              <b>DEMONSTRATION OUTPUT ONLY.</b><br>
              Placeholder coefficients are used only to demonstrate the interface. This is not a clinically validated AMBER result.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="soft">
              <b style="color:#06285F">Derived biomarker features calculated successfully.</b><br><br>
              A validated probability is not shown because no locked PET-trained AMBER model has been loaded.
            </div>
            """, unsafe_allow_html=True)

        if st.session_state.amber_report is not None:
            st.write("")
            st.download_button(
                "Download research summary (.json)",
                data=json.dumps(st.session_state.amber_report, indent=2),
                file_name="AMBER_V01_research_summary.json",
                mime="application/json",
                use_container_width=True,
            )

    st.markdown('<div class="section-title">What happens after you click Calculate?</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="flow">
      <div class="flow-card">
        <div class="flow-num">1</div>
        <div class="flow-title">Read inputs</div>
        <div class="flow-body">Aβ40 and Aβ42 are taken as measured concentrations; age and sex are used only for AMBER-C.</div>
      </div>
      <div class="arrow">→</div>
      <div class="flow-card">
        <div class="flow-num">2</div>
        <div class="flow-title">Derive features</div>
        <div class="flow-body">The app calculates Aβ42/Aβ40, R and M internally to avoid manual mismatch.</div>
      </div>
      <div class="arrow">→</div>
      <div class="flow-card">
        <div class="flow-num">3</div>
        <div class="flow-title">Apply model</div>
        <div class="flow-body">A future locked model will convert these features into a calibrated pathology probability.</div>
      </div>
      <div class="arrow">→</div>
      <div class="flow-card">
        <div class="flow-num">4</div>
        <div class="flow-title">Report</div>
        <div class="flow-body">The result is presented with model status and reproducible research metadata.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 3. METHOD
# ============================================================
elif page == "DNA Compass / Method":
    st.markdown('<div class="kicker">Nanotechnology layer</div><div class="page-title">Integrated molecular workflow</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="soft">
      <b style="color:#06285F">Purpose of this page</b><br><br>
      To show the molecular-to-computational architecture directly in the web interface, while keeping unpublished
      sequences, precise geometry, fabrication parameters and other patent-sensitive implementation details outside the public app.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">DNA Compass → AMBER</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="mol-wrap">
      <div class="mol-flow">
        <div class="mol-step">
          <div class="mol-symbol">01</div>
          <div class="mol-title">Plasma</div>
          <div class="mol-body">Blood-derived research sample.</div>
        </div>
        <div class="mol-step">
          <div class="mol-symbol">02</div>
          <div class="mol-title">DNA Compass</div>
          <div class="mol-body">Programmable molecular recognition architecture.</div>
        </div>
        <div class="mol-step">
          <div class="mol-symbol">03</div>
          <div class="mol-title">Aβ40 + Aβ42</div>
          <div class="mol-body">Simultaneous selective acquisition of the two amyloid peptides.</div>
        </div>
        <div class="mol-step">
          <div class="mol-symbol">04</div>
          <div class="mol-title">Optical readout</div>
          <div class="mol-body">Quantitative reporter signal converted into concentrations.</div>
        </div>
        <div class="mol-step">
          <div class="mol-symbol">05</div>
          <div class="mol-title">Transform</div>
          <div class="mol-body">Ratio, R and M are derived computationally.</div>
        </div>
        <div class="mol-step">
          <div class="mol-symbol">06</div>
          <div class="mol-title">AMBER</div>
          <div class="mol-body">Future PET-trained model estimates cerebral amyloid positivity.</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("""
        <div class="panel">
          <h3>Why Aβ40 and Aβ42?</h3>
          <div style="color:#5F7288;line-height:1.55">
            The project focuses on the direct amyloid molecular pair because the intended reference endpoint is cerebral amyloid deposition.
            The key modelling question is whether retaining both measured dimensions adds reproducible value beyond the conventional ratio alone.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="panel">
          <h3>Contemporary comparator</h3>
          <div style="color:#5F7288;line-height:1.55">
            p-tau217 can be included as a contemporary comparator where available.
            AMBER does not need to claim universal superiority of Aβ42/Aβ40 over p-tau217.
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="notice">
      <b>Public-disclosure boundary:</b> exact DNA sequences, architecture dimensions, fabrication parameters,
      recognition chemistry and other potentially novel implementation details are intentionally not displayed here.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 4. VALIDATION
# ============================================================
elif page == "Model & Validation":
    st.markdown('<div class="kicker">Evidence framework</div><div class="page-title">Future validation dashboard</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="notice">
      <b>No performance metrics are claimed in V0.1.</b>
      These are real dashboard components in an empty state, ready to receive future PET-linked validation outputs.
    </div>
    """, unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3, gap="large")

    with d1:
        roc = go.Figure()
        roc.add_trace(go.Scatter(
            x=[0,1], y=[0,1],
            mode="lines",
            line=dict(dash="dash"),
            name="Chance"
        ))
        roc.update_layout(
            title="ROC / AUROC",
            xaxis_title="1 − Specificity",
            yaxis_title="Sensitivity",
            xaxis=dict(range=[0,1]),
            yaxis=dict(range=[0,1]),
            height=360,
            margin=dict(l=45,r=20,t=55,b=45),
            paper_bgcolor="white",
            plot_bgcolor="#FAFCFF",
            showlegend=False,
            annotations=[dict(
                x=.5,y=.58,xref="paper",yref="paper",
                text="<b>Awaiting PET-linked hospital data</b><br>No AUROC is calculated in V0.1",
                showarrow=False,font=dict(size=14,color="#6C7E93")
            )]
        )
        st.plotly_chart(roc, use_container_width=True)

    with d2:
        cal = go.Figure()
        cal.add_trace(go.Scatter(
            x=[0,1], y=[0,1],
            mode="lines",
            line=dict(dash="dash"),
            name="Ideal"
        ))
        cal.update_layout(
            title="Calibration",
            xaxis_title="Predicted probability",
            yaxis_title="Observed probability",
            xaxis=dict(range=[0,1]),
            yaxis=dict(range=[0,1]),
            height=360,
            margin=dict(l=45,r=20,t=55,b=45),
            paper_bgcolor="white",
            plot_bgcolor="#FAFCFF",
            showlegend=False,
            annotations=[dict(
                x=.5,y=.58,xref="paper",yref="paper",
                text="<b>Awaiting model derivation</b><br>Intercept · slope · plot · Brier score",
                showarrow=False,font=dict(size=14,color="#6C7E93")
            )]
        )
        st.plotly_chart(cal, use_container_width=True)

    with d3:
        dca = go.Figure()
        dca.add_hline(y=0, line_dash="dash")
        dca.update_layout(
            title="Decision-curve analysis",
            xaxis_title="Threshold probability",
            yaxis_title="Net benefit",
            xaxis=dict(range=[0,1]),
            yaxis=dict(range=[-.1,.2]),
            height=360,
            margin=dict(l=45,r=20,t=55,b=45),
            paper_bgcolor="white",
            plot_bgcolor="#FAFCFF",
            showlegend=False,
            annotations=[dict(
                x=.5,y=.58,xref="paper",yref="paper",
                text="<b>Awaiting prespecified operating thresholds</b><br>No net-benefit curve is calculated in V0.1",
                showarrow=False,font=dict(size=14,color="#6C7E93")
            )]
        )
        st.plotly_chart(dca, use_container_width=True)

    st.markdown('<div class="section-title">Prespecified model comparison</div>', unsafe_allow_html=True)
    df = pd.DataFrame([
        ["Aβ40 alone", "Single-biomarker comparator"],
        ["Aβ42 alone", "Single-biomarker comparator"],
        ["Aβ42/Aβ40 ratio", "Conventional ratio comparator"],
        ["AMBER-B (R + M)", "Primary joint biomarker model"],
        ["AMBER-C (R + M + age + sex)", "Clinical extension if incremental value is reproducible"],
        ["p-tau217", "Optional contemporary comparator"],
        ["p-tau217/Aβ42", "Optional comparator"],
    ], columns=["Model / biomarker", "Purpose"])
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.write("")
    st.markdown("""
    <div class="info">
      <b>Model-lock principle:</b> preprocessing, coefficients, calibration and operating thresholds
      must be frozen before independent external validation. Any later recalibration becomes a new model version.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 5. ABOUT
# ============================================================
else:
    st.markdown('<div class="kicker">Scientific information</div><div class="page-title">About AMBER</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="soft">
      <b style="color:#06285F;font-size:1.05rem">AMBER is a research architecture, not yet a clinical diagnostic product.</b><br><br>
      Its purpose is to integrate DNA Compass molecular measurement with transparent computational modelling
      and later PET-linked validation in a reproducible research platform.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Development sequence</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="timeline">
      <div class="tstep">
        <div class="tnum">1</div>
        <div class="ttitle">App</div>
        <div class="tbody">Finalize the best research-oriented user interface and computational architecture.</div>
        <span class="tstatus">Current</span>
      </div>
      <div class="tstep">
        <div class="tnum">2</div>
        <div class="ttitle">Patent</div>
        <div class="tbody">Define the protectable DNA Compass + AMBER technical architecture and prepare filing documents.</div>
        <span class="tstatus">Next</span>
      </div>
      <div class="tstep">
        <div class="tnum">3</div>
        <div class="ttitle">Hospital data</div>
        <div class="tbody">Obtain paired Aβ40, Aβ42 and amyloid PET outcome data under the approved study design.</div>
        <span class="tstatus">Future</span>
      </div>
      <div class="tstep">
        <div class="tnum">4</div>
        <div class="ttitle">Validation</div>
        <div class="tbody">Use the Colab scientific pipeline for derivation, bootstrap validation, calibration and external validation.</div>
        <span class="tstatus">Future</span>
      </div>
      <div class="tstep">
        <div class="tnum">5</div>
        <div class="ttitle">Update</div>
        <div class="tbody">Load the frozen validated model artifact into the AMBER application and release the new version.</div>
        <span class="tstatus">After evidence</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("""
        <div class="panel">
          <h3>Project</h3>
          <b>A Project by</b><br>Fahim ElKassim<br><br>
          <b>Supervised by</b><br>Prof. Xingyi Ma<br>NanoMax Group, HIT Shenzhen
        </div>
        """, unsafe_allow_html=True)
    with right:
        st.markdown("""
        <div class="panel">
          <h3>Development</h3>
          <b>Designed and Developed by</b><br>Doctor Sukhera（学睿）<br><br>
          <b>Version</b><br>AMBER V0.1 · Research Prototype
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="notice">
      <b>IP note:</b> potentially novel DNA Compass engineering details should remain outside the public application until institutional patent filing is complete.
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    f'<div class="footer"><div><b>{APP_VERSION}</b></div><div>Model status: {MODEL_STATUS}</div><div>Research use only · Not a diagnostic test</div></div>',
    unsafe_allow_html=True
)
