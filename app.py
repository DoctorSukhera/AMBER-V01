import math
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="AMBER V0.1", page_icon="🧪", layout="wide", initial_sidebar_state="collapsed")

APP_VERSION = "AMBER V0.1"
APP_STATUS = "FINAL FRONTEND PROTOTYPE"
MODEL_STATUS = "DEMONSTRATION ONLY"
ASSAY_STATUS = "PROTOTYPE SPECIFICATION"

AB40_RANGE = (20.0, 2000.0)
AB42_RANGE = (2.0, 200.0)

# DEMONSTRATION COEFFICIENTS ONLY — NOT CLINICALLY DERIVED
DEMO_B = {"intercept": -1.40, "R": -1.00, "M": 0.18}
DEMO_C = {"intercept": -1.70, "R": -1.10, "M": 0.20, "age": 0.012, "sex": 0.15}

st.markdown("""
<style>
:root{
 --navy:#071D49;--navy2:#0A2F69;--blue:#123F96;--gold:#F5B82E;
 --line:#DCE5F4;--softblue:#F1F6FF;--warn:#FFF8E7;--danger:#FFF0F0;
}
.block-container{max-width:1480px;padding-top:.75rem;padding-bottom:2rem}
header[data-testid="stHeader"]{background:rgba(255,255,255,.94);backdrop-filter:blur(8px)}
.top{background:linear-gradient(105deg,var(--navy),var(--navy2));color:#fff;border-radius:19px;padding:21px 27px;margin-bottom:12px;box-shadow:0 8px 26px rgba(7,29,73,.12)}
.toprow{display:flex;align-items:center;gap:15px}
.logo{width:54px;height:54px;border-radius:50%;border:2px solid var(--gold);display:flex;align-items:center;justify-content:center;color:var(--gold);font-weight:900;font-size:1.12rem;flex:0 0 54px}
.brand{font-size:2rem;font-weight:850;line-height:1;letter-spacing:-.03em}.brand .amber{color:var(--gold)}
.subtitle{margin-top:.42rem;opacity:.93;font-size:.98rem}
.badges{margin-top:.72rem;display:flex;gap:.45rem;flex-wrap:wrap}
.badge{display:inline-block;padding:.34rem .68rem;border-radius:999px;background:#EEF4FF;color:#0A2F69;font-size:.73rem;font-weight:850}
.kicker{color:var(--blue);font-size:.73rem;font-weight:850;text-transform:uppercase;letter-spacing:.065em}
.title{color:var(--navy);font-size:1.62rem;font-weight:850;margin:.18rem 0 .85rem}
.hero{border:1px solid var(--line);border-radius:18px;padding:29px 31px;background:linear-gradient(120deg,#fff 0%,#F3F7FF 100%);box-shadow:0 3px 14px rgba(20,63,150,.04)}
.hero h1{color:var(--navy);font-size:2.45rem;line-height:1.13;letter-spacing:-.035em;margin:.12rem 0 .8rem}
.hero p{color:#38465F;line-height:1.6;font-size:1rem;max-width:980px}
.card{border:1px solid var(--line);border-radius:16px;padding:17px 18px;background:#fff;height:100%;box-shadow:0 3px 12px rgba(20,63,150,.03)}
.icon{width:40px;height:40px;border-radius:12px;background:#EEF4FF;display:flex;align-items:center;justify-content:center;color:#123F96;font-size:1.1rem;margin-bottom:.7rem}
.cardtitle{color:var(--navy);font-weight:850;font-size:1rem;margin-bottom:.3rem}
.cardbody{color:#4E5C74;line-height:1.52;font-size:.91rem}
.metricbox{border:1px solid var(--line);border-radius:14px;background:white;padding:13px;text-align:center}
.metricname{color:#6C778B;font-size:.74rem;font-weight:750}
.metricvalue{color:var(--navy);font-size:1.5rem;font-weight:850;margin-top:.16rem}
.notice{border:1px solid #EED599;background:var(--warn);color:#78550E;border-radius:13px;padding:13px 15px}
.info{border:1px solid #CCDEFF;background:var(--softblue);color:#123F96;border-radius:13px;padding:13px 15px}
.danger{border:1px solid #F2C5C5;background:var(--danger);color:#9A3030;border-radius:13px;padding:13px 15px}
.placeholder{border:1px dashed #B9C7E3;border-radius:16px;min-height:180px;display:flex;align-items:center;justify-content:center;text-align:center;background:#FBFCFF;color:#667085;padding:20px}
.eqpanel{border:1px solid var(--line);border-radius:15px;background:#FBFCFF;padding:14px 16px}
.footer{border-top:1px solid var(--line);margin-top:24px;padding-top:12px;color:#778296;font-size:.77rem;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
div[data-testid="stSegmentedControl"] button{font-weight:700}
</style>
""", unsafe_allow_html=True)

def card(icon, title, body):
    return f'<div class="card"><div class="icon">{icon}</div><div class="cardtitle">{title}</div><div class="cardbody">{body}</div></div>'

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
    p = sigmoid(I)
    return ratio, R, M, I, p*100

st.markdown("""
<div class="top">
  <div class="toprow">
    <div class="logo">Aβ</div>
    <div>
      <div class="brand"><span class="amber">AMBER</span> Score Platform</div>
      <div class="subtitle">Blood-based research platform for estimation of cerebral amyloid positivity.</div>
    </div>
  </div>
  <div class="badges">
    <span class="badge">V0.1</span>
    <span class="badge">FINAL FRONTEND PROTOTYPE</span>
    <span class="badge">DEMONSTRATION ONLY</span>
  </div>
</div>
""", unsafe_allow_html=True)

pages = ["Home","AMBER Calculator","DNA Compass / Method","Model & Validation","Longitudinal Monitoring","About / Scientific Information"]
page = st.segmented_control("Navigation", pages, default="Home", label_visibility="collapsed")
if page is None:
    page = "Home"

if page == "Home":
    st.markdown('<div class="kicker">Molecular measurement → biological interpretation</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h1>From blood biomarkers to probability<br>of cerebral amyloid positivity</h1>
      <p>
        AMBER is being developed to connect simultaneous plasma Aβ40 and Aβ42 measurements
        with transparent computational inference of cerebral amyloid pathology.
        V0.1 is the finalized frontend prototype and demonstrates workflow, scientific transparency,
        and model-integration architecture without claiming clinical validation.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    a,b,c = st.columns(3, gap="large")
    with a: st.markdown(card("01","Measure","Acquire quantitative plasma Aβ40 and Aβ42 using the DNA Compass analytical workflow."), unsafe_allow_html=True)
    with b: st.markdown(card("02","Transform","Compute Aβ42/Aβ40 and the relative-composition (R) and abundance (M) terms."), unsafe_allow_html=True)
    with c: st.markdown(card("03","Estimate","Apply a future locked model to estimate individualized cerebral amyloid probability."), unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="title">How AMBER works</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    steps = [("1","Sample","Plasma specimen"),("2","DNA Compass","Dual acquisition"),("3","Aβ40 + Aβ42","Measured inputs"),("4","Transform","Ratio, R, M"),("5","Inference","AMBER-B / C"),("6","Output","Amyloid probability")]
    for col,(n,h,t) in zip(cols,steps):
        with col:
            st.markdown(f'<div class="card"><div class="cardtitle">{n}. {h}</div><div class="cardbody">{t}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>Prototype status:</b> no clinically derived coefficients, calibration, operating thresholds, ROC curves, or external-validation metrics are included in V0.1.</div>', unsafe_allow_html=True)

elif page == "AMBER Calculator":
    st.markdown('<div class="kicker">Core workflow</div><div class="title">AMBER Calculator</div>', unsafe_allow_html=True)

    demo_enabled = st.toggle("Enable illustrative demo mode", value=False, help="Demo mode uses placeholder coefficients only to test the interface.")
    if not demo_enabled:
        st.markdown('<div class="info"><b>Demo mode is off.</b> This is the scientifically safest default. A validated AMBER probability will only become available after real PET-linked model derivation and validation.</div>', unsafe_allow_html=True)

    st.write("")
    left,center,right = st.columns([.95,1.25,1], gap="large")

    with left:
        st.markdown("### 1. Input values")
        model_name = st.selectbox("Model configuration", ["AMBER-B (biomarker-only)","AMBER-C (biomarker + age/sex)"])
        ab40 = st.number_input("Plasma Aβ40 (pg/mL)", min_value=.01, value=285.0, step=1.0, format="%.2f")
        st.caption("Prototype interface range: 20–2000 pg/mL")
        ab42 = st.number_input("Plasma Aβ42 (pg/mL)", min_value=.01, value=18.5, step=.1, format="%.2f")
        st.caption("Prototype interface range: 2–200 pg/mL")
        amber_b = model_name.startswith("AMBER-B")
        age = st.number_input("Age (years)", min_value=18, max_value=100, value=68, disabled=amber_b)
        sex = st.radio("Sex", ["Male","Female"], horizontal=True, index=1, disabled=amber_b)
        run = st.button("Calculate illustrative score", type="primary", use_container_width=True, disabled=not demo_enabled)
        st.caption("Aβ42/Aβ40, R and M are always derived internally.")

    with center:
        st.markdown("### 2. Result")
        if not demo_enabled:
            st.markdown('<div class="placeholder"><div><b>Validated AMBER model not yet loaded</b><br><br>Future state:<br>measured biomarkers → locked model → calibrated probability</div></div>', unsafe_allow_html=True)
        elif run:
            ratio,R,M,I,score = demo_predict(model_name,ab40,ab42,age,sex)
            if not (AB40_RANGE[0] <= ab40 <= AB40_RANGE[1]): st.warning("Aβ40 is outside the current prototype interface range.")
            if not (AB42_RANGE[0] <= ab42 <= AB42_RANGE[1]): st.warning("Aβ42 is outside the current prototype interface range.")

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={"suffix":"/100","font":{"size":52,"color":"#071D49"}},
                title={"text":"Illustrative software output"},
                gauge={"axis":{"range":[0,100]},"bar":{"color":"#0A2F69","thickness":.22},"steps":[{"range":[0,100],"color":"#EEF3FA"}]}
            ))
            fig.update_layout(height=330,margin=dict(l=25,r=25,t=45,b=5),paper_bgcolor="white")
            st.plotly_chart(fig,use_container_width=True)

            st.markdown('<div class="danger"><b>NOT A CLINICALLY DERIVED AMBER SCORE.</b><br>Demonstration coefficients are used only to test the interface and calculation pathway.</div>', unsafe_allow_html=True)

            st.write("")
            m1,m2,m3 = st.columns(3)
            with m1: st.markdown(f'<div class="metricbox"><div class="metricname">Aβ42/Aβ40</div><div class="metricvalue">{ratio:.4f}</div></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metricbox"><div class="metricname">R</div><div class="metricvalue">{R:.3f}</div></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metricbox"><div class="metricname">M</div><div class="metricvalue">{M:.3f}</div></div>', unsafe_allow_html=True)

            report = f"""AMBER V0.1 — FRONTEND PROTOTYPE
Generated: {datetime.now().isoformat(timespec='minutes')}
Status: DEMONSTRATION ONLY

Model configuration: {model_name}
Aβ40: {ab40:.2f} pg/mL
Aβ42: {ab42:.2f} pg/mL
Age: {'Not used' if amber_b else age}
Sex: {'Not used' if amber_b else sex}

Derived values
Aβ42/Aβ40: {ratio:.6f}
R: {R:.6f}
M: {M:.6f}

Illustrative score: {score:.2f}/100

WARNING:
This result is generated from placeholder demonstration coefficients.
It is NOT clinically validated.
"""
            st.download_button("Download prototype summary", report, "AMBER_V01_prototype_summary.txt", "text/plain", use_container_width=True)
        else:
            st.markdown('<div class="placeholder"><div><b>Demo mode enabled</b><br><br>Enter values and select Calculate illustrative score.</div></div>', unsafe_allow_html=True)

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
        st.markdown('<div class="notice"><b>Future locked model:</b> final coefficients, calibration, and decision thresholds must come from real outcome-labelled clinical data and independent validation.</div>', unsafe_allow_html=True)

elif page == "DNA Compass / Method":
    st.markdown('<div class="kicker">Molecular acquisition architecture</div><div class="title">DNA Compass / Method</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h1 style="font-size:2rem;">DNA Compass–enabled dual-biomarker measurement</h1>
      <p>The intended AMBER architecture couples quantitative acquisition of plasma Aβ40 and Aβ42 to transparent computational interpretation of cerebral amyloid positivity. The public V0.1 deliberately avoids unpublished assay-engineering details.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    cols = st.columns(6)
    method = [("01","Sample","Plasma specimen"),("02","DNA Compass","Programmable recognition"),("03","Aβ42 + Aβ40","Simultaneous acquisition"),("04","Readout","Quantitative signal"),("05","Transform","Ratio, R and M"),("06","AMBER","Probability inference")]
    for col,(ic,h,t) in zip(cols,method):
        with col: st.markdown(card(ic,h,t), unsafe_allow_html=True)

    st.write("")
    l,r = st.columns(2,gap="large")
    with l:
        st.markdown("### Biomarker transformations")
        st.latex(r"\mathrm{Ratio}=\frac{A\beta42}{A\beta40}")
        st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
    with r:
        st.markdown("### Why Aβ42 and Aβ40?")
        st.write("AMBER tests whether simultaneous quantitative information from the two amyloid peptides can be translated into a calibrated estimate of cerebral amyloid pathology, and whether retaining both measurements adds reproducible information beyond the ratio alone.")
        st.markdown('<div class="info"><b>Contemporary context:</b> the project does not assume superiority over p-tau217. Where feasible, p-tau217 can be included as a contemporary comparator.</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>IP safeguard:</b> exact DNA sequences, architecture, fabrication parameters, recognition chemistry, and unpublished implementation details are intentionally excluded from the public prototype.</div>', unsafe_allow_html=True)

elif page == "Model & Validation":
    st.markdown('<div class="kicker">Evidence layer</div><div class="title">Model & Validation</div>', unsafe_allow_html=True)
    st.markdown('<div class="notice"><b>No AMBER performance metrics are claimed in V0.1.</b> This page is reserved for future real-data validation outputs.</div>', unsafe_allow_html=True)

    st.write("")
    p1,p2,p3 = st.columns(3,gap="large")
    with p1: st.markdown('<div class="placeholder"><div><b>ROC / discrimination</b><br>Awaiting outcome-labelled clinical data</div></div>', unsafe_allow_html=True)
    with p2: st.markdown('<div class="placeholder"><div><b>Calibration</b><br>Awaiting model derivation and validation</div></div>', unsafe_allow_html=True)
    with p3: st.markdown('<div class="placeholder"><div><b>Decision-curve analysis</b><br>Awaiting locked clinical operating thresholds</div></div>', unsafe_allow_html=True)

    st.write("")
    df = pd.DataFrame([
        ["Aβ40 alone","Planned","Single-biomarker comparator"],
        ["Aβ42 alone","Planned","Single-biomarker comparator"],
        ["Aβ42/Aβ40 ratio","Planned","Conventional ratio comparator"],
        ["AMBER-B","Planned","Primary biomarker-only model"],
        ["AMBER-C","Planned","Prespecified age/sex extension"],
        ["p-tau217","Optional","Contemporary comparator if available"],
        ["p-tau217/Aβ42","Optional","Contemporary ratio comparator if available"],
    ], columns=["Model / biomarker","Status","Purpose"])
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.write("")
    a,b,c = st.columns(3,gap="large")
    with a: st.markdown(card("A","Discrimination","AUROC with confidence intervals, sensitivity, specificity, PPV, and NPV at locked thresholds."), unsafe_allow_html=True)
    with b: st.markdown(card("B","Calibration","Calibration intercept/slope, calibration plot, and Brier score."), unsafe_allow_html=True)
    with c: st.markdown(card("C","Clinical utility","Decision-curve analysis and prespecified rule-out / rule-in operating strategies."), unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="info"><b>Model-lock principle:</b> preprocessing, coefficients, calibration, and thresholds must be frozen before independent external validation.</div>', unsafe_allow_html=True)

elif page == "Longitudinal Monitoring":
    st.markdown('<div class="kicker">Future research module</div><div class="title">Longitudinal Monitoring</div>', unsafe_allow_html=True)
    st.markdown('<div class="info"><b>Reserved in V0.1.</b> This module becomes scientifically active only after repeated-measure data and an appropriate longitudinal validation framework are available.</div>', unsafe_allow_html=True)

    st.write("")
    left,right = st.columns([1.6,1],gap="large")
    with left:
        fig = go.Figure()
        fig.update_xaxes(title="Visit / time", showgrid=True, gridcolor="#E8EDF6")
        fig.update_yaxes(title="AMBER probability", range=[0,100], showgrid=True, gridcolor="#E8EDF6")
        fig.add_annotation(x=.5,y=.52,xref="paper",yref="paper",text="<b>No longitudinal dataset loaded</b><br>Interface preview only",showarrow=False,font=dict(size=18,color="#667085"))
        fig.update_layout(height=380,paper_bgcolor="white",plot_bgcolor="#FBFCFF",margin=dict(l=35,r=20,t=20,b=35))
        st.plotly_chart(fig,use_container_width=True)

    with right:
        st.markdown(card("01","Trajectory view","Future repeated Aβ40, Aβ42, ratio, and validated AMBER probability trajectories."), unsafe_allow_html=True)
        st.write("")
        st.markdown(card("02","Assay metadata","Track assay version, batch, collection date, and longitudinal QC context."), unsafe_allow_html=True)
        st.write("")
        st.markdown(card("03","Research export","Export repeated-measure records for validated longitudinal statistical analysis."), unsafe_allow_html=True)

else:
    st.markdown('<div class="kicker">Scientific information</div><div class="title">About AMBER</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h1 style="font-size:2rem;">A molecular-to-pathology research architecture</h1>
      <p>AMBER is being developed to connect nanoscale molecular measurement with probabilistic assessment of cerebral amyloid pathology. V0.1 is the finalized frontend prototype and does not contain a clinically derived AMBER equation.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    a,b,c = st.columns(3,gap="large")
    with a: st.markdown(card("01","Intended research use","Support assay-development studies, model derivation, validation, reproducible computation, and future longitudinal research."), unsafe_allow_html=True)
    with b: st.markdown(card("02","What AMBER is not","Not currently an Alzheimer's disease diagnosis, stand-alone diagnostic test, or substitute for PET, CSF testing, or clinical assessment."), unsafe_allow_html=True)
    with c: st.markdown(card("03","Current status","Application: V0.1 final frontend prototype. Model: demonstration only. Clinical coefficients and thresholds: not yet derived."), unsafe_allow_html=True)

    st.write("")
    st.markdown("### Scientific development path")
    cols = st.columns(6)
    roadmap = [("1","Analytical","DNA Compass validation"),("2","Clinical","PET-linked cohort"),("3","Derivation","AMBER-B / C"),("4","Internal","Bootstrap validation"),("5","Lock","Freeze model"),("6","External","Independent validation")]
    for col,(n,h,t) in zip(cols,roadmap):
        with col: st.markdown(f'<div class="card"><div class="cardtitle">{n}. {h}</div><div class="cardbody">{t}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>IP / disclosure note:</b> potentially novel assay-engineering details should remain outside the public application until institutional intellectual-property review and patent filing strategy are complete.</div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer"><div><b>{APP_VERSION}</b> · {APP_STATUS}</div><div>Model: {MODEL_STATUS} · Assay: {ASSAY_STATUS}</div><div>Research use only · Not a diagnostic test</div></div>', unsafe_allow_html=True)
