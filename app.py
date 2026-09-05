import json
import math
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="AMBER Score Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "AMBER V0.1"
MODEL_STATUS = "DEMONSTRATION ONLY"

# PLACEHOLDER COEFFICIENTS — NOT CLINICALLY DERIVED.
DEMO_B = {"intercept": -1.40, "R": -1.00, "M": 0.18}
DEMO_C = {"intercept": -1.70, "R": -1.10, "M": 0.20, "age": 0.012, "sex": 0.15}

st.markdown("""
<style>
:root{
  --navy:#06285F;
  --navy2:#0B3D8A;
  --gold:#F3B42C;
  --blue:#1565C0;
  --cyan:#30A7D8;
  --ink:#13233F;
  --muted:#62738A;
  --line:#D7E3F1;
  --pale:#F6FAFF;
  --pale2:#EEF5FD;
  --warn:#FFF9E9;
  --danger:#FFF1F1;
}
html,body,[class*="css"]{
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
.stApp{background:#fff;color:var(--ink)}
.block-container{max-width:1540px;padding-top:3.8rem!important;padding-bottom:2rem}
header[data-testid="stHeader"]{background:rgba(255,255,255,.96);border-bottom:1px solid #EEF3F7}

.hero{
  background:linear-gradient(105deg,#031D48 0%,#06285F 62%,#0B3D8A 100%);
  color:white;border-radius:0 0 24px 24px;padding:22px 30px 25px;margin:-1rem 0 1.1rem;
  box-shadow:0 14px 30px rgba(5,40,95,.12)
}
.hero-brand{display:flex;align-items:center;gap:18px}
.hero-logo{width:68px;height:68px;object-fit:contain;filter:brightness(0) invert(1)}
.hero-title{font-size:2.32rem;line-height:1;font-weight:850;letter-spacing:-.035em}
.hero-title .amber{color:var(--gold)}
.hero-sub{color:#E7EFFA;margin-top:.42rem;font-size:1rem;line-height:1.45}
.badges{display:flex;gap:.4rem;flex-wrap:wrap;margin-top:.78rem}
.badge{padding:.29rem .62rem;border-radius:999px;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.15);font-size:.69rem;font-weight:750;color:white}

div[data-testid="stSegmentedControl"]{margin-bottom:1rem}
div[data-testid="stSegmentedControl"] button{border-radius:9px!important;font-weight:750!important;min-height:40px}
div[data-testid="stSegmentedControl"] button[aria-checked="true"]{
  background:#FFF5D9!important;color:var(--navy)!important;border-color:#E8C567!important
}

.page-kicker{color:var(--navy2);font-size:.72rem;font-weight:850;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.22rem}
.page-title{color:var(--navy);font-size:1.72rem;font-weight:850;margin-bottom:.9rem}
.panel{border:1px solid var(--line);border-radius:16px;padding:20px;background:#fff;box-shadow:0 7px 18px rgba(28,76,121,.05);height:100%}
.subpanel{border:1px solid #C9DBEE;border-radius:14px;padding:14px 16px;background:linear-gradient(180deg,#FBFDFF,#F2F7FD)}
.section-title{color:var(--navy);font-size:1.35rem;font-weight:850;margin:1.05rem 0 .65rem}
.help{border:1px solid #BCD5EF;background:#F2F7FE;color:#234D7D;border-radius:12px;padding:12px 14px;font-size:.9rem}
.notice{border:1px solid #ECD8A6;background:var(--warn);color:#6B561B;border-radius:12px;padding:12px 14px}
.danger{border:1px solid #F0C8C8;background:var(--danger);color:#9B3232;border-radius:12px;padding:12px 14px}
.placeholder{min-height:300px;border:1px dashed #AFC4DC;border-radius:16px;background:#FAFCFF;display:flex;align-items:center;justify-content:center;text-align:center;color:#6C7E93;padding:22px}
.metric-card{border:1px solid var(--line);border-radius:13px;padding:12px;background:#fff;text-align:center}
.metric-name{color:#77889D;font-size:.72rem;font-weight:750}
.metric-value{color:var(--navy);font-weight:850;font-size:1.5rem;margin-top:.15rem}
.eqpanel{border:1px solid var(--line);border-radius:15px;background:#FAFCFE;padding:14px 16px}
.figure-card{border:1px solid var(--line);border-radius:16px;padding:12px;background:#fff;box-shadow:0 7px 18px rgba(28,76,121,.04)}
.figure-card img{border-radius:11px}
.footer{border-top:1px solid var(--line);margin-top:1.4rem;padding-top:.8rem;color:#7D8D9E;font-size:.74rem;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px}
.stButton>button{background:linear-gradient(90deg,#06285F,#0B3D8A);color:white;border:none;border-radius:10px;font-weight:850;min-height:46px}
.stDownloadButton>button{background:#fff;color:var(--navy);border:1px solid #BDD2E9;border-radius:10px;font-weight:750}
h1,h2,h3,h4{color:var(--navy)!important}
</style>
""", unsafe_allow_html=True)

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
        I = c["intercept"] + c["R"]*R + c["M"]*M + c["age"]*age + c["sex"]*(1 if sex=="Female" else 0)
    return ratio, R, M, sigmoid(I)*100

def header():
    logo = "assets/hitsz_logo.png"
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-brand">
            <img class="hero-logo" src="data:image/png;base64,{_logo_b64}" alt="HIT Shenzhen">
            <div>
              <div class="hero-title"><span class="amber">AMBER</span> Score Platform</div>
              <div class="hero-sub">Blood-based molecular research platform for estimation of cerebral amyloid positivity.</div>
            </div>
          </div>
          <div class="badges">
            <span class="badge">V0.1 · RESEARCH PROTOTYPE</span>
            <span class="badge">DNA COMPASS + COMPUTATIONAL INFERENCE</span>
            <span class="badge">NO CLINICAL VALIDATION CLAIMS</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

import base64
try:
    with open("assets/hitsz_logo.png","rb") as f:
        _logo_b64 = base64.b64encode(f.read()).decode("ascii")
except Exception:
    _logo_b64 = ""

header()

pages = ["Home","AMBER Calculator","DNA Compass / Method","Model & Validation","About AMBER"]
page = st.segmented_control("Navigation", pages, default="Home", label_visibility="collapsed") or "Home"

# ============================================================
# PAGE 1 — HOME
# ============================================================
if page == "Home":
    st.markdown('<div class="page-kicker">Research concept</div><div class="page-title">A focused molecular-to-pathology research platform</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="subpanel">
      <b style="color:#06285F;font-size:1.06rem">Main scientific question</b><br><br>
      Can simultaneous blood-based measurement of Aβ40 and Aβ42, enabled by a programmable DNA Compass assay,
      support a transparent and eventually validated estimate of PET-defined cerebral amyloid positivity?
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Why AMBER is needed and how it works</div>', unsafe_allow_html=True)
    st.markdown('<div class="figure-card">', unsafe_allow_html=True)
    st.image("assets/home_visual.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="notice">
      <b>Current stage:</b> the application and research workflow are being finalized before patent preparation.
      Clinical coefficients, thresholds, and performance claims will only be added after PET-linked hospital-data derivation and validation.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE 2 — CALCULATOR
# ============================================================
elif page == "AMBER Calculator":
    st.markdown('<div class="page-kicker">Core computational interface</div><div class="page-title">AMBER Calculator</div>', unsafe_allow_html=True)

    with st.form("amber_form"):
        left, mid, right = st.columns([1,1.05,1], gap="large")

        with left:
            st.markdown("### 1. INPUT VALUES")
            model_name = st.selectbox("Model configuration", ["AMBER-B (biomarker-only)","AMBER-C (biomarker + age/sex)"])
            amber_b = model_name.startswith("AMBER-B")

            if not amber_b:
                st.markdown("#### Demographics")
                age = st.number_input("Age (years)",18,100,68)
                sex = st.radio("Sex",["Male","Female"],horizontal=True,index=1)
            else:
                age = 68
                sex = "Female"

            st.markdown("#### Biomarker measurements")
            ab40 = st.number_input("Plasma Aβ40 concentration (pg/mL)", min_value=.01, value=285.0, step=1.0, format="%.2f")
            ab42 = st.number_input("Plasma Aβ42 concentration (pg/mL)", min_value=.01, value=18.5, step=.1, format="%.2f")

            demo = st.checkbox("Use illustrative demo probability", value=False)
            submitted = st.form_submit_button("CALCULATE AMBER SCORE", use_container_width=True)

        with mid:
            st.markdown("### 2. RESULTS")
            if submitted:
                ratio, R, M = derive(ab40, ab42)
                m1,m2,m3 = st.columns(3)
                with m1:
                    st.markdown(f'<div class="metric-card"><div class="metric-name">Aβ42/Aβ40</div><div class="metric-value">{ratio:.4f}</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-card"><div class="metric-name">R</div><div class="metric-value">{R:.3f}</div></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-card"><div class="metric-name">M</div><div class="metric-value">{M:.3f}</div></div>', unsafe_allow_html=True)

                st.write("")
                if demo:
                    ratio, R, M, score = demo_predict(model_name, ab40, ab42, age, sex)
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=score,
                        number={"suffix":"/100","font":{"size":56,"color":"#06285F"}},
                        title={"text":"Illustrative AMBER output"},
                        gauge={
                            "axis":{"range":[0,100]},
                            "bar":{"color":"#0B3D8A","thickness":.20},
                            "steps":[{"range":[0,100],"color":"#EDF5FA"}],
                        }
                    ))
                    fig.update_layout(height=330,margin=dict(l=18,r=18,t=50,b=0),paper_bgcolor="white")
                    st.plotly_chart(fig,use_container_width=True)
                    st.markdown('<div class="danger"><b>DEMONSTRATION OUTPUT ONLY.</b><br>This is not a clinically validated AMBER score.</div>', unsafe_allow_html=True)

                    report = {
                        "application":APP_VERSION,
                        "generated_at":datetime.now().isoformat(timespec="minutes"),
                        "status":"DEMONSTRATION ONLY",
                        "configuration":model_name,
                        "ab40_pg_ml":ab40,
                        "ab42_pg_ml":ab42,
                        "age":None if amber_b else age,
                        "sex":None if amber_b else sex,
                        "ratio":ratio,
                        "R":R,
                        "M":M,
                        "illustrative_score":score,
                    }
                    st.download_button(
                        "Download demonstration research summary",
                        json.dumps(report,indent=2),
                        "AMBER_V01_demo.json",
                        "application/json",
                        use_container_width=True
                    )
                else:
                    st.markdown("""
                    <div class="placeholder">
                      <div>
                        <b style="color:#06285F">Derived biomarker features calculated successfully.</b><br><br>
                        A validated probability is unavailable because no locked PET-trained AMBER model has been loaded.
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="placeholder">
                  <div>
                    Enter the research inputs and click<br><b>CALCULATE AMBER SCORE</b>.<br><br>
                    Nothing is calculated automatically.
                  </div>
                </div>
                """, unsafe_allow_html=True)

        with right:
            st.markdown("### 3. SCIENTIFIC BASIS")
            st.markdown('<div class="eqpanel">', unsafe_allow_html=True)
            st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
            st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
            st.markdown("**AMBER-B**")
            st.latex(r"I_B=\beta_0+\beta_RR+\beta_MM")
            st.markdown("**AMBER-C**")
            st.latex(r"I_C=\beta_0+\beta_RR+\beta_MM+\beta_A Age+\beta_S Sex")
            st.latex(r"P=\frac{1}{1+e^{-I}}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Calculator workflow</div>', unsafe_allow_html=True)
    st.markdown('<div class="figure-card">', unsafe_allow_html=True)
    st.image("assets/calculator_visual.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PAGE 3 — METHOD
# ============================================================
elif page == "DNA Compass / Method":
    st.markdown('<div class="page-kicker">Nanotechnology layer</div><div class="page-title">DNA Compass / Method</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="subpanel">
      <b style="color:#06285F">Scientific purpose</b><br><br>
      This page explains the physical-to-computational chain of AMBER while deliberately excluding unpublished
      DNA sequences, precise geometry, fabrication parameters, and other potentially patent-relevant implementation details.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Integrated molecular workflow</div>', unsafe_allow_html=True)
    st.markdown('<div class="figure-card">', unsafe_allow_html=True)
    st.image("assets/method_visual.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PAGE 4 — VALIDATION
# ============================================================
elif page == "Model & Validation":
    st.markdown('<div class="page-kicker">Evidence framework</div><div class="page-title">Model & Validation</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="notice">
      <b>No AMBER performance metrics are claimed in V0.1.</b>
      The dashboard below is a live empty-state scientific interface. It will populate only after real PET-linked data are analyzed.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Future validation dashboard</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3,gap="large")

    # ROC empty state
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1],y=[0,1],mode="lines",line=dict(dash="dash"),name="Chance"))
        fig.update_layout(
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
                showarrow=False,font=dict(size=15,color="#6C7E93")
            )]
        )
        st.plotly_chart(fig,use_container_width=True)

    # Calibration empty state
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1],y=[0,1],mode="lines",line=dict(dash="dash"),name="Perfect calibration"))
        fig.update_layout(
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
                showarrow=False,font=dict(size=15,color="#6C7E93")
            )]
        )
        st.plotly_chart(fig,use_container_width=True)

    # DCA empty state
    with c3:
        fig = go.Figure()
        fig.add_hline(y=0,line_dash="dash")
        fig.update_layout(
            title="Decision-curve analysis",
            xaxis_title="Threshold probability",
            yaxis_title="Net benefit",
            xaxis=dict(range=[0,1]),
            yaxis=dict(range=[-0.1,.2]),
            height=360,
            margin=dict(l=45,r=20,t=55,b=45),
            paper_bgcolor="white",
            plot_bgcolor="#FAFCFF",
            showlegend=False,
            annotations=[dict(
                x=.5,y=.58,xref="paper",yref="paper",
                text="<b>Awaiting prespecified operating thresholds</b><br>No net-benefit curve is calculated in V0.1",
                showarrow=False,font=dict(size=15,color="#6C7E93")
            )]
        )
        st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-title">Planned model comparison</div>', unsafe_allow_html=True)
    df = pd.DataFrame([
        ["Aβ40 alone","Single-biomarker comparator"],
        ["Aβ42 alone","Single-biomarker comparator"],
        ["Aβ42/Aβ40 ratio","Conventional ratio comparator"],
        ["AMBER-B (R + M)","Primary joint biomarker model"],
        ["AMBER-C (R + M + age + sex)","Clinical extension if incremental value is reproducible"],
        ["p-tau217","Optional contemporary comparator"],
        ["p-tau217/Aβ42","Optional comparator"],
    ], columns=["Model / biomarker","Purpose"])
    st.dataframe(df,hide_index=True,use_container_width=True)

# ============================================================
# PAGE 5 — ABOUT
# ============================================================
else:
    st.markdown('<div class="page-kicker">Scientific information</div><div class="page-title">About AMBER</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="subpanel">
      <b style="color:#06285F;font-size:1.05rem">AMBER is a research architecture, not yet a clinical diagnostic product.</b><br><br>
      It integrates DNA Compass molecular measurement with transparent computational modelling and later PET-linked validation.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Development sequence</div>', unsafe_allow_html=True)
    st.markdown('<div class="figure-card">', unsafe_allow_html=True)
    st.image("assets/development_visual.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    a,b = st.columns(2,gap="large")
    with a:
        st.markdown("""
        <div class="panel">
          <h3>Project</h3>
          <b>A Project by</b><br>Fahim ElKassim<br><br>
          <b>Supervised by</b><br>Prof. Xingyi Ma<br>NanoMax Group, HIT Shenzhen
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel">
          <h3>Development</h3>
          <b>Designed and Developed by</b><br>Doctor Sukhera（学睿）<br><br>
          <b>Version</b><br>AMBER V0.1 · Research Prototype
        </div>
        """, unsafe_allow_html=True)

st.markdown(
    f'<div class="footer"><div><b>{APP_VERSION}</b></div><div>Model status: {MODEL_STATUS}</div><div>Research use only · Not a diagnostic test</div></div>',
    unsafe_allow_html=True
)
