import json
import math
import base64
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

LOGO_PATH = "assets/hitsz_logo.png"
try:
    with open(LOGO_PATH, "rb") as _f:
        HIT_LOGO_B64 = base64.b64encode(_f.read()).decode("ascii")
except Exception:
    HIT_LOGO_B64 = ""

# Placeholder coefficients — software demonstration only.
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
  --green:#59B52C;
  --yellow:#FFBF2F;
  --orange:#F28A2B;
  --red:#EB3C39;
  --ink:#13233F;
  --muted:#62738A;
  --line:#D7E3F1;
  --pale:#F6FAFF;
  --pale2:#EEF5FD;
}

html,body,[class*="css"]{
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
.stApp{
  background:#FFFFFF;
  color:var(--ink);
}
.block-container{
  max-width:1540px;
  padding-top:3.7rem !important;
  padding-bottom:2rem;
}
header[data-testid="stHeader"]{
  background:rgba(255,255,255,.96);
  border-bottom:1px solid #EEF3F7;
}

/* HERO */
.hero{
  background:linear-gradient(105deg,#031D48 0%,#06285F 62%,#0B3D8A 100%);
  color:white;
  border-radius:0 0 24px 24px;
  padding:24px 30px 27px;
  margin:-1rem 0 1.25rem;
  box-shadow:0 14px 30px rgba(5,40,95,.12);
}
.hero-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:20px;
}
.hero-brand{
  display:flex;
  align-items:center;
  gap:18px;
}
.institution-logo{
  width:72px;
  max-height:72px;
  object-fit:contain;
  filter:brightness(0) invert(1);
  opacity:.98;
}
.logo-mark{
  width:64px;height:64px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  border:2px solid var(--gold);
  color:var(--gold);
  font-size:1.35rem;
  font-weight:900;
  background:rgba(255,255,255,.03);
}
.hero-title{
  font-size:2.42rem;
  line-height:1;
  font-weight:850;
  letter-spacing:-.035em;
}
.hero-title .amber{color:var(--gold)}
.hero-sub{
  color:#E7EFFA;
  margin-top:.42rem;
  font-size:1rem;
  line-height:1.45;
}
.hero-badges{
  display:flex;
  gap:.45rem;
  flex-wrap:wrap;
  margin-top:.85rem;
}
.badge{
  padding:.32rem .68rem;
  border-radius:999px;
  background:rgba(255,255,255,.1);
  border:1px solid rgba(255,255,255,.16);
  font-size:.72rem;
  font-weight:750;
  color:white;
}

/* top nav */
div[data-testid="stSegmentedControl"]{
  margin-bottom:1.05rem;
}
div[data-testid="stSegmentedControl"] button{
  border-radius:10px !important;
  font-weight:750 !important;
  min-height:42px;
}

/* panels */
.page-kicker{
  color:var(--navy2);
  font-size:.73rem;
  font-weight:850;
  text-transform:uppercase;
  letter-spacing:.08em;
  margin-bottom:.25rem;
}
.page-title{
  color:var(--navy);
  font-size:1.7rem;
  font-weight:850;
  margin-bottom:.9rem;
}
.panel{
  border:1px solid var(--line);
  border-radius:16px;
  padding:20px;
  background:white;
  box-shadow:0 7px 18px rgba(28,76,121,.05);
  height:100%;
}
.panel h3{
  color:var(--navy)!important;
  margin-top:0;
}
.subpanel{
  border:1px solid #C9DBEE;
  border-radius:14px;
  padding:14px 16px;
  background:linear-gradient(180deg,#FBFDFF,#F2F7FD);
}
.section-title{
  color:var(--navy);
  font-size:1.38rem;
  font-weight:850;
  margin:1.1rem 0 .7rem;
}
.help{
  border:1px solid #BCD5EF;
  background:#F2F7FE;
  color:#234D7D;
  border-radius:12px;
  padding:12px 14px;
  font-size:.9rem;
}
.notice{
  border:1px solid #ECD8A6;
  background:#FFF9E9;
  color:#6B561B;
  border-radius:12px;
  padding:12px 14px;
}
.danger{
  border:1px solid #F0C8C8;
  background:#FFF1F1;
  color:#9B3232;
  border-radius:12px;
  padding:12px 14px;
}
.placeholder{
  min-height:325px;
  border:1px dashed #AFC4DC;
  border-radius:16px;
  background:#FAFCFF;
  display:flex;
  align-items:center;
  justify-content:center;
  text-align:center;
  color:#6C7E93;
  padding:22px;
}
.metric-card{
  border:1px solid var(--line);
  border-radius:13px;
  padding:12px;
  background:#fff;
  text-align:center;
}
.metric-name{
  color:#77889D;
  font-size:.72rem;
  font-weight:750;
}
.metric-value{
  color:var(--navy);
  font-weight:850;
  font-size:1.5rem;
  margin-top:.15rem;
}
.formula-note{
  color:#4B6077;
  font-size:.88rem;
  line-height:1.55;
}
.research-card{
  border:1px solid var(--line);
  border-radius:15px;
  padding:17px;
  background:white;
  height:100%;
  box-shadow:0 5px 16px rgba(30,75,117,.04);
}
.rc-num{
  width:34px;height:34px;border-radius:10px;
  background:#EDF4FD;color:var(--navy2);
  display:flex;align-items:center;justify-content:center;
  font-weight:850;margin-bottom:.6rem;
}
.rc-title{
  color:var(--navy);font-weight:850;margin-bottom:.3rem;
}
.rc-body{
  color:#5A6D82;font-size:.9rem;line-height:1.5;
}
.footer{
  border-top:1px solid var(--line);
  margin-top:1.5rem;
  padding-top:.9rem;
  color:#7D8D9E;
  font-size:.76rem;
  display:flex;
  justify-content:space-between;
  flex-wrap:wrap;
  gap:12px;
}

/* inputs */
div[data-testid="stNumberInput"] input,
div[data-baseweb="select"] > div{
  border-radius:10px !important;
}
.stButton>button{
  background:linear-gradient(90deg,#06285F,#0B3D8A);
  color:white;
  border:none;
  border-radius:10px;
  font-weight:850;
  min-height:44px;
}
.stDownloadButton>button{
  background:white;
  color:var(--navy);
  border:1px solid #BDD2E9;
  border-radius:10px;
  font-weight:750;
}
h1,h2,h3,h4{color:var(--navy)!important}
</style>
""", unsafe_allow_html=True)

def derive(ab40, ab42):
    ratio = ab42/ab40
    R = math.log10(ratio)
    M = math.log10(math.sqrt(ab40*ab42))
    return ratio,R,M

def sigmoid(x):
    if x >= 0:
        z = math.exp(-x)
        return 1/(1+z)
    z = math.exp(x)
    return z/(1+z)

def demo_predict(model_name, ab40, ab42, age, sex):
    ratio,R,M = derive(ab40,ab42)
    if model_name.startswith("AMBER-B"):
        c = DEMO_B
        I = c["intercept"] + c["R"]*R + c["M"]*M
    else:
        c = DEMO_C
        I = c["intercept"] + c["R"]*R + c["M"]*M + c["age"]*age + c["sex"]*(1 if sex=="Female" else 0)
    return ratio,R,M,sigmoid(I)*100

def research_card(n,title,body):
    return f'<div class="research-card"><div class="rc-num">{n}</div><div class="rc-title">{title}</div><div class="rc-body">{body}</div></div>'

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

logo_html = (
    f'<img class="institution-logo" src="data:image/png;base64,{HIT_LOGO_B64}" alt="HIT Shenzhen logo">'
    if HIT_LOGO_B64
    else '<div class="logo-mark">Aβ</div>'
)
st.markdown(f"""
<div class="hero">
  <div class="hero-top">
    <div class="hero-brand">
      {logo_html}
      <div>
        <div class="hero-title"><span class="amber">AMBER</span> Score Platform</div>
        <div class="hero-sub">Blood-based molecular research platform for estimation of cerebral amyloid positivity.</div>
      </div>
    </div>
  </div>
  <div class="hero-badges">
    <span class="badge">V0.1 · RESEARCH PROTOTYPE</span>
    <span class="badge">DNA COMPASS + COMPUTATIONAL INFERENCE</span>
    <span class="badge">NO CLINICAL VALIDATION CLAIMS</span>
  </div>
</div>
""", unsafe_allow_html=True)

pages = ["Home","AMBER Calculator","DNA Compass / Method","Model & Validation","About AMBER"]
page = st.segmented_control("Navigation", pages, default="Home", label_visibility="collapsed")
if page is None:
    page = "Home"

# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------
if page == "Home":
    st.markdown('<div class="page-kicker">Research concept</div><div class="page-title">A focused molecular-to-pathology research platform</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="subpanel">
      <b style="color:#06285F;font-size:1.08rem">Main scientific question</b><br><br>
      Can simultaneous blood-based measurement of Aβ40 and Aβ42, enabled by a programmable DNA Compass assay,
      support a transparent and eventually validated estimate of PET-defined cerebral amyloid positivity?
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">AMBER research logic</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5,gap="large")
    with c1: st.markdown(research_card("1","Measure","Acquire Aβ40 and Aβ42 quantitatively through the DNA Compass sensing workflow."),unsafe_allow_html=True)
    with c2: st.markdown(research_card("2","Transform","Derive Aβ42/Aβ40 plus the interpretable R and M coordinate representation."),unsafe_allow_html=True)
    with c3: st.markdown(research_card("3","Model","Compare ratio-only, AMBER-B, and the prespecified AMBER-C clinical extension."),unsafe_allow_html=True)
    with c4: st.markdown(research_card("4","Validate","Use PET-linked hospital data for discrimination, calibration and clinical-utility analysis."),unsafe_allow_html=True)
    with c5: st.markdown(research_card("5","Translate","Load only a frozen validated model into the production AMBER interface."),unsafe_allow_html=True)

    st.markdown('<div class="section-title">What makes AMBER scientifically interesting?</div>', unsafe_allow_html=True)
    a,b,c = st.columns(3,gap="large")
    with a:
        st.markdown("""
        <div class="panel">
          <h3>Molecular acquisition</h3>
          <div class="formula-note">
          The innovation begins upstream of the calculator: a programmable DNA Compass architecture is intended to acquire both highly related amyloid peptides in one analytical system.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel">
          <h3>Information preservation</h3>
          <div class="formula-note">
          AMBER tests whether the joint two-biomarker information adds reproducible value beyond collapsing both measurements into the conventional Aβ42/Aβ40 ratio alone.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c:
        st.markdown("""
        <div class="panel">
          <h3>Pathology-linked inference</h3>
          <div class="formula-note">
          The clinical target is cerebral amyloid positivity, preferably defined by amyloid PET — not a stand-alone Alzheimer's disease diagnosis.
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>Current stage:</b> the software workflow is being finalized before patent preparation. Clinical coefficients and performance will only be added after real hospital-data derivation and validation.</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# CALCULATOR
# ------------------------------------------------------------
elif page == "AMBER Calculator":
    st.markdown('<div class="page-kicker">Core computational interface</div><div class="page-title">AMBER Calculator</div>', unsafe_allow_html=True)

    left,mid,right = st.columns([1,1.02,1],gap="large")

    with left:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        st.markdown("### 1. INPUT VALUES")
        st.caption("Enter biomarker values and, for AMBER-C, demographic variables.")

        model_name = st.selectbox("Model configuration",["AMBER-B (biomarker-only)","AMBER-C (biomarker + age/sex)"])
        amber_b = model_name.startswith("AMBER-B")

        st.markdown("#### Demographics")
        age = st.number_input("Age (years)",18,100,68,disabled=amber_b)
        sex = st.radio("Sex",["Male","Female"],horizontal=True,index=1,disabled=amber_b)

        st.markdown("---")
        st.markdown("#### Biomarker measurements")
        ab40 = st.number_input("Plasma Aβ40 concentration (pg/mL)",min_value=.01,value=285.0,step=1.0,format="%.2f")
        ab42 = st.number_input("Plasma Aβ42 concentration (pg/mL)",min_value=.01,value=18.5,step=.1,format="%.2f")

        st.markdown('<div class="help">Aβ40 and Aβ42 should be obtained from the same locked analytical workflow and reported in compatible units.</div>',unsafe_allow_html=True)

        ratio,R,M = derive(ab40,ab42)
        st.write("")
        d1,d2,d3 = st.columns(3)
        with d1: st.markdown(f'<div class="metric-card"><div class="metric-name">Aβ42/Aβ40</div><div class="metric-value">{ratio:.4f}</div></div>',unsafe_allow_html=True)
        with d2: st.markdown(f'<div class="metric-card"><div class="metric-name">R</div><div class="metric-value">{R:.3f}</div></div>',unsafe_allow_html=True)
        with d3: st.markdown(f'<div class="metric-card"><div class="metric-name">M</div><div class="metric-value">{M:.3f}</div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    with mid:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        st.markdown("### 2. RESULTS")
        demo = st.toggle("Enable illustrative probability",value=False)

        if not demo:
            st.markdown("""
            <div class="placeholder">
              <div>
                <b style="font-size:1.05rem;color:#06285F">Validated AMBER model not yet loaded</b><br><br>
                The final probability layer will only be activated after:<br><br>
                hospital Aβ40/Aβ42 + amyloid PET data<br>
                → model derivation<br>
                → bootstrap validation<br>
                → model lock<br>
                → independent external validation
              </div>
            </div>
            """,unsafe_allow_html=True)
        else:
            ratio,R,M,score = demo_predict(model_name,ab40,ab42,age,sex)

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={"suffix":"/100","font":{"size":58,"color":"#06285F"}},
                title={"text":"Illustrative AMBER output"},
                gauge={
                    "axis":{"range":[0,100],"tickwidth":1},
                    "bar":{"color":"#0B3D8A","thickness":.20},
                    "steps":[
                        {"range":[0,25],"color":"#67B82E"},
                        {"range":[25,50],"color":"#B9CE28"},
                        {"range":[50,75],"color":"#FFBF2F"},
                        {"range":[75,100],"color":"#EB3C39"},
                    ]
                }
            ))
            fig.update_layout(height=340,margin=dict(l=18,r=18,t=50,b=0),paper_bgcolor="white")
            st.plotly_chart(fig,use_container_width=True)

            st.markdown('<div class="danger"><b>DEMONSTRATION OUTPUT ONLY.</b><br>The colored spectrum is visual only and does not represent validated AMBER clinical cutoffs.</div>',unsafe_allow_html=True)

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
            st.write("")
            st.download_button("Download demonstration research summary",json.dumps(report,indent=2),"AMBER_V01_demo.json","application/json",use_container_width=True)

        st.markdown('</div>',unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        st.markdown("### 3. ABOUT THE AMBER SCORE")
        st.write("AMBER is designed to translate jointly measured Aβ40 and Aβ42 into a future calibrated probability of cerebral amyloid positivity.")

        st.markdown('<div class="subpanel">',unsafe_allow_html=True)
        st.markdown("#### How the score is structured")
        st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
        st.markdown("**AMBER-B**")
        st.latex(r"I_B=\beta_0+\beta_RR+\beta_MM")
        st.markdown("**AMBER-C**")
        st.latex(r"I_C=\beta_0+\beta_RR+\beta_MM+\beta_A Age+\beta_S Sex")
        st.latex(r"P=\frac{1}{1+e^{-I}}")
        st.markdown('</div>',unsafe_allow_html=True)

        st.write("")
        st.markdown("""
        <div class="notice">
        <b>Scientific safeguard:</b> no final β coefficients, clinical thresholds, AUC, sensitivity, specificity, or model-lock date are shown until they are empirically derived and validated.
        </div>
        """,unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

# ------------------------------------------------------------
# METHOD
# ------------------------------------------------------------
elif page == "DNA Compass / Method":
    st.markdown('<div class="page-kicker">Nanotechnology layer</div><div class="page-title">DNA Compass / Method</div>',unsafe_allow_html=True)

    st.markdown("""
    <div class="subpanel">
      <b style="color:#06285F">Scientific purpose</b><br><br>
      This page explains the physical-to-computational chain of AMBER without exposing unpublished sequences,
      assay geometry, fabrication parameters, or other potentially patent-relevant implementation details.
    </div>
    """,unsafe_allow_html=True)

    st.markdown('<div class="section-title">Integrated molecular workflow</div>',unsafe_allow_html=True)
    cols = st.columns(6,gap="large")
    for col,(n,h,t) in zip(cols,[
        ("1","Plasma","Blood-derived sample"),
        ("2","DNA Compass","Programmable recognition"),
        ("3","Aβ40 + Aβ42","Simultaneous acquisition"),
        ("4","Optical readout","Quantitative signal"),
        ("5","Transform","Ratio, R and M"),
        ("6","AMBER","PET-linked probability"),
    ]):
        with col:
            st.markdown(research_card(n,h,t),unsafe_allow_html=True)

    st.write("")
    a,b = st.columns(2,gap="large")
    with a:
        st.markdown("""
        <div class="panel">
          <h3>Why Aβ40 and Aβ42?</h3>
          <div class="formula-note">
          The project focuses on the direct amyloid molecular pair because the intended reference endpoint is cerebral amyloid deposition.
          The main computational question is whether retaining both measured dimensions improves upon a ratio-only model.
          </div>
        </div>
        """,unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="panel">
          <h3>Contemporary comparator</h3>
          <div class="formula-note">
          p-tau217 can be included as a contemporary comparator if available in the clinical study.
          AMBER should not claim that Aβ42/Aβ40 is universally superior to p-tau217.
          </div>
        </div>
        """,unsafe_allow_html=True)

# ------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------
elif page == "Model & Validation":
    st.markdown('<div class="page-kicker">Evidence framework</div><div class="page-title">Model & Validation</div>',unsafe_allow_html=True)

    st.markdown("""
    <div class="notice">
      <b>No performance metrics are claimed in V0.1.</b>
      This page predefines the analyses that will populate the platform once PET-linked hospital data are available.
    </div>
    """,unsafe_allow_html=True)

    st.markdown('<div class="section-title">Prespecified model comparison</div>',unsafe_allow_html=True)
    df = pd.DataFrame([
        ["Aβ40 alone","Single-biomarker comparator"],
        ["Aβ42 alone","Single-biomarker comparator"],
        ["Aβ42/Aβ40 ratio","Conventional ratio comparator"],
        ["AMBER-B (R + M)","Primary joint biomarker model"],
        ["AMBER-C (R + M + age + sex)","Clinical extension if incremental value is reproducible"],
        ["p-tau217","Optional contemporary comparator"],
        ["p-tau217/Aβ42","Optional comparator"],
    ],columns=["Model / biomarker","Purpose"])
    st.dataframe(df,hide_index=True,use_container_width=True)

    st.markdown('<div class="section-title">Future validation dashboard</div>',unsafe_allow_html=True)
    p1,p2,p3 = st.columns(3,gap="large")
    with p1:
        st.markdown('<div class="placeholder"><div><b>ROC / AUROC</b><br><br>Awaiting PET-linked hospital data</div></div>',unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="placeholder"><div><b>Calibration</b><br><br>Intercept · slope · plot · Brier score</div></div>',unsafe_allow_html=True)
    with p3:
        st.markdown('<div class="placeholder"><div><b>Decision-curve analysis</b><br><br>Awaiting prespecified operating thresholds</div></div>',unsafe_allow_html=True)

    st.write("")
    a,b,c = st.columns(3,gap="large")
    with a: st.markdown(research_card("A","Discrimination","AUROC with confidence intervals and paired comparisons where appropriate."),unsafe_allow_html=True)
    with b: st.markdown(research_card("B","Calibration","Calibration intercept/slope, calibration plot, and Brier score."),unsafe_allow_html=True)
    with c: st.markdown(research_card("C","Clinical utility","Decision-curve analysis and locked rule-out / rule-in strategies."),unsafe_allow_html=True)

# ------------------------------------------------------------
# ABOUT
# ------------------------------------------------------------
else:
    st.markdown('<div class="page-kicker">Scientific information</div><div class="page-title">About AMBER</div>',unsafe_allow_html=True)

    st.markdown("""
    <div class="subpanel">
      <b style="color:#06285F;font-size:1.08rem">AMBER is a research architecture, not yet a clinical diagnostic product.</b><br><br>
      Its purpose is to integrate DNA Compass molecular measurement with transparent computational modelling
      and later PET-linked validation in a reproducible research platform.
    </div>
    """,unsafe_allow_html=True)

    st.markdown('<div class="section-title">Scope</div>',unsafe_allow_html=True)
    a,b,c = st.columns(3,gap="large")
    with a: st.markdown(research_card("1","What AMBER is","A molecular-to-pathology research platform linking dual amyloid measurement to future probabilistic inference."),unsafe_allow_html=True)
    with b: st.markdown(research_card("2","What AMBER is not","Not currently an Alzheimer's disease diagnosis, a stand-alone clinical diagnostic test, or a substitute for PET/CSF assessment."),unsafe_allow_html=True)
    with c: st.markdown(research_card("3","Current stage","Frontend architecture is being finalized first; patent preparation follows, then hospital-data model derivation and validation."),unsafe_allow_html=True)

    st.markdown('<div class="section-title">Development sequence</div>',unsafe_allow_html=True)
    cols = st.columns(5,gap="large")
    for col,(n,h,t) in zip(cols,[
        ("1","App","Best research UI"),
        ("2","Patent","Protect invention"),
        ("3","Hospital data","Aβ40/Aβ42 + PET"),
        ("4","Validation","Colab pipeline"),
        ("5","Update","Load locked model"),
    ]):
        with col:
            st.markdown(research_card(n,h,t),unsafe_allow_html=True)

    st.write("")
    c1,c2 = st.columns([1,1],gap="large")
    with c1:
        st.markdown("""
        <div class="panel">
          <h3>Project</h3>
          <div class="formula-note">
            <b>A Project by</b><br>Fahim ElKassim<br><br>
            <b>Supervised by</b><br>Prof. Xingyi Ma<br>NanoMax Group, HIT Shenzhen
          </div>
        </div>
        """,unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="panel">
          <h3>Development</h3>
          <div class="formula-note">
            <b>Designed and Developed by</b><br>Doctor Sukhera（学睿）<br><br>
            <b>Version</b><br>AMBER V0.1 · Research Prototype
          </div>
        </div>
        """,unsafe_allow_html=True)

st.markdown(f'<div class="footer"><div><b>{APP_VERSION}</b></div><div>Model status: {MODEL_STATUS}</div><div>Research use only · Not a diagnostic test</div></div>',unsafe_allow_html=True)
