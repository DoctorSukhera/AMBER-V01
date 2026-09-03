
import json
import math
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="AMBER V0.1",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "AMBER V0.1"
MODEL_STATUS = "DEMONSTRATION ONLY"

# Placeholder coefficients only. These are not clinically derived.
DEMO_B = {"intercept": -1.40, "R": -1.00, "M": 0.18}
DEMO_C = {"intercept": -1.70, "R": -1.10, "M": 0.20, "age": 0.012, "sex": 0.15}

st.markdown(r'''
<style>
:root{
 --navy:#0B2F5B;
 --blue:#1666A8;
 --cyan:#21A7C7;
 --line:#D6E4EF;
 --text:#183247;
 --muted:#61778A;
 --pale:#F4F9FD;
 --warn:#FFF8E7;
 --danger:#FFF1F1;
}
.stApp{background:linear-gradient(180deg,#FFFFFF 0%,#F8FBFD 100%);color:var(--text)}
.block-container{max-width:1450px;padding-top:3.8rem !important;padding-bottom:2rem}
header[data-testid="stHeader"]{background:rgba(255,255,255,.96);border-bottom:1px solid #EEF3F7}

section[data-testid="stSidebar"]{
 background:linear-gradient(180deg,#F8FCFE 0%,#EEF6FB 100%);
 border-right:1px solid var(--line);
}
section[data-testid="stSidebar"] > div{padding-top:1rem}
.side-title{text-align:center;color:var(--navy);font-weight:850;font-size:1.2rem;margin-top:.15rem}
.side-sub{text-align:center;color:var(--muted);font-size:.75rem;line-height:1.45;margin:.25rem 0 1rem}

section[data-testid="stSidebar"] div[role="radiogroup"]{gap:.32rem}
section[data-testid="stSidebar"] div[role="radiogroup"] label{
 background:#fff;border:1px solid var(--line);padding:.55rem .65rem;border-radius:10px;color:var(--text)
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){
 background:#EAF5FB;border-color:#71BBD2;box-shadow:inset 3px 0 0 var(--cyan);color:var(--navy)
}
section[data-testid="stSidebar"] div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{
 font-weight:750;font-size:.9rem
}

.credit-card{
 margin-top:1.2rem;border:1px solid var(--line);border-radius:14px;padding:13px 14px;background:white;
 color:var(--text);font-size:.77rem;line-height:1.45
}
.credit-card .label{color:#8294A2;font-size:.68rem;text-transform:uppercase;letter-spacing:.04em}
.credit-card .name{font-weight:800;color:var(--navy);margin-bottom:.52rem}
.credit-card .group{color:var(--blue)}

.hero{
 background:linear-gradient(120deg,#F8FCFF,#EDF7FC);border:1px solid var(--line);border-radius:20px;
 padding:31px 32px;box-shadow:0 10px 28px rgba(35,89,126,.06);margin-bottom:1rem
}
.kicker{color:var(--blue);font-weight:850;text-transform:uppercase;letter-spacing:.09em;font-size:.71rem}
.hero h1{color:var(--navy);font-size:2.45rem;line-height:1.12;letter-spacing:-.035em;margin:.45rem 0 .75rem}
.hero p{color:#3E586B;line-height:1.65;font-size:1rem;max-width:1030px}
.pillrow{display:flex;gap:.45rem;flex-wrap:wrap;margin-top:.85rem}
.pill{display:inline-block;padding:.34rem .68rem;border-radius:999px;background:white;border:1px solid #CFE2EE;color:var(--blue);font-size:.72rem;font-weight:750}
.section-title{color:var(--navy);font-size:1.55rem;font-weight:850;margin:.3rem 0 .85rem}
.card{border:1px solid var(--line);border-radius:16px;padding:18px;background:#fff;min-height:145px;height:100%;box-shadow:0 5px 18px rgba(31,85,121,.04)}
.icon{width:38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;color:var(--blue);border:1px solid #CFE2EE;background:#F2F9FC;font-weight:850;margin-bottom:.72rem}
.cardtitle{color:var(--navy);font-weight:830;margin-bottom:.35rem}
.cardbody{color:#5B7183;font-size:.9rem;line-height:1.52}
.info{border-left:3px solid var(--cyan);background:#F0F8FC;color:#31566C;border-radius:0 12px 12px 0;padding:13px 15px}
.notice{border:1px solid #E7D49E;background:var(--warn);color:#6F5920;border-radius:13px;padding:13px 15px}
.danger{border:1px solid #F0CACA;background:var(--danger);color:#9A3030;border-radius:13px;padding:13px 15px}
.placeholder{border:1px dashed #AFC9DA;border-radius:16px;min-height:185px;display:flex;align-items:center;justify-content:center;text-align:center;background:#FAFCFE;color:#6F8190;padding:20px}
.metricbox{border:1px solid var(--line);border-radius:13px;background:white;padding:13px;text-align:center}
.metricname{color:#7A8D9B;font-size:.72rem;font-weight:750}
.metricvalue{color:var(--navy);font-size:1.45rem;font-weight:850;margin-top:.15rem}
.eqpanel{border:1px solid var(--line);border-radius:15px;background:#FAFCFE;padding:14px 16px}
.footer{border-top:1px solid var(--line);margin-top:24px;padding-top:12px;color:#7A8B99;font-size:.75rem;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.stButton > button{background:linear-gradient(90deg,#1579B5,#20A8C8);color:white;border:none;border-radius:10px;font-weight:800}
.stDownloadButton > button{background:white;color:var(--navy);border:1px solid #BDD4E1;border-radius:10px;font-weight:700}
h1,h2,h3,h4{color:var(--navy) !important}
p,li,label{color:var(--text)}
</style>
''', unsafe_allow_html=True)

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
        return 1/(1+z)
    z = math.exp(x)
    return z/(1+z)

def demo_predict(model_name, ab40, ab42, age, sex):
    ratio, R, M = derive(ab40, ab42)
    if model_name.startswith("AMBER-B"):
        c = DEMO_B
        I = c["intercept"] + c["R"]*R + c["M"]*M
    else:
        c = DEMO_C
        I = c["intercept"] + c["R"]*R + c["M"]*M + c["age"]*age + c["sex"]*(1 if sex=="Female" else 0)
    return ratio, R, M, sigmoid(I)*100

def hero(title, body, kicker, pills):
    pill_html = "".join([f'<span class="pill">{p}</span>' for p in pills])
    st.markdown(
        f'<div class="hero"><div class="kicker">{kicker}</div><h1>{title}</h1><p>{body}</p><div class="pillrow">{pill_html}</div></div>',
        unsafe_allow_html=True
    )

with st.sidebar:
    st.image("assets/hitsz_logo.png", use_container_width=True)
    st.markdown(
        '<div class="side-title">AMBER Research Platform</div><div class="side-sub">Blood biomarker sensing → transparent molecular interpretation</div>',
        unsafe_allow_html=True
    )

    nav = st.radio(
        "Navigation",
        ["Home","AMBER Calculator","DNA Compass / Method","Model & Validation","About AMBER"],
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="credit-card">'
        '<div class="label">A Project by</div><div class="name">Fahim ElKassim</div>'
        '<div class="label">Supervised by</div><div class="name">Prof. Xingyi Ma<br><span class="group">NanoMax Group, HIT Shenzhen</span></div>'
        '<div class="label">Designed and Developed by</div><div class="name">Doctor Sukhera（学睿）</div>'
        '</div>',
        unsafe_allow_html=True
    )

if nav == "Home":
    hero(
        "Can dual-amyloid blood sensing inform cerebral amyloid pathology?",
        "AMBER is a research platform built around a focused scientific question: whether simultaneous quantitative measurement of plasma Aβ40 and Aβ42 can be transformed into a transparent and eventually validated estimate of cerebral amyloid positivity.",
        "RESEARCH CONCEPT",
        ["Aβ40 + Aβ42","DNA Compass","Ratio / R / M","PET-linked validation","Research-use prototype"],
    )

    a,b,c = st.columns(3, gap="large")
    with a:
        st.markdown(card("01","Sensing question","Can a programmable molecular-recognition system measure Aβ40 and Aβ42 together with sufficient analytical precision?"), unsafe_allow_html=True)
    with b:
        st.markdown(card("02","Information question","Does retaining both biomarker dimensions provide reproducible value beyond reducing them to Aβ42/Aβ40 alone?"), unsafe_allow_html=True)
    with c:
        st.markdown(card("03","Pathology question","Can the resulting molecular information support a calibrated probability of PET-defined cerebral amyloid positivity?"), unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-title">Core AMBER workflow</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for col,(n,h,t) in zip(cols,[
        ("1","Measure","Aβ40 + Aβ42"),
        ("2","Transform","Ratio, R and M"),
        ("3","Model","AMBER-B / AMBER-C"),
        ("4","Validate","PET-linked cohorts"),
        ("5","Translate","Research probability output"),
    ]):
        with col:
            st.markdown(card(n,h,t), unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>Current stage:</b> software and scientific architecture only. No clinical performance, coefficients, thresholds, or diagnostic claims are made in V0.1.</div>', unsafe_allow_html=True)

elif nav == "AMBER Calculator":
    hero(
        "AMBER Calculator",
        "The calculator demonstrates the intended computational pathway. Aβ42/Aβ40, R and M are valid mathematical transformations; the clinical probability remains disabled unless illustrative demo mode is deliberately enabled.",
        "COMPUTATIONAL WORKFLOW",
        ["Measured Aβ40","Measured Aβ42","Internal transformations","AMBER-B","AMBER-C"],
    )

    left,center,right = st.columns([.95,1.2,1], gap="large")

    with left:
        st.markdown("### 1. Research inputs")
        model_name = st.selectbox("Model configuration", ["AMBER-B (biomarker-only)","AMBER-C (biomarker + age/sex)"])
        ab40 = st.number_input("Plasma Aβ40 (pg/mL)", min_value=.01, value=280.0, step=1.0, format="%.2f")
        ab42 = st.number_input("Plasma Aβ42 (pg/mL)", min_value=.01, value=18.5, step=.1, format="%.2f")
        amber_b = model_name.startswith("AMBER-B")
        age = st.number_input("Age (years)",18,100,68,disabled=amber_b)
        sex = st.radio("Sex",["Male","Female"],horizontal=True,index=1,disabled=amber_b)

        ratio,R,M = derive(ab40,ab42)
        st.write("")
        st.markdown("**Derived from the measured biomarkers**")
        m1,m2,m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metricbox"><div class="metricname">Aβ42/Aβ40</div><div class="metricvalue">{ratio:.4f}</div></div>',unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metricbox"><div class="metricname">R</div><div class="metricvalue">{R:.3f}</div></div>',unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metricbox"><div class="metricname">M</div><div class="metricvalue">{M:.3f}</div></div>',unsafe_allow_html=True)

    with center:
        st.markdown("### 2. Probability layer")
        demo_enabled = st.toggle("Enable illustrative demo probability", value=False)
        if not demo_enabled:
            st.markdown(
                '<div class="placeholder"><div><b>Validated probability model not yet loaded</b><br><br>'
                'Real hospital data + amyloid PET outcome<br>→ model derivation<br>→ internal validation<br>'
                '→ model lock<br>→ external validation<br>→ validated AMBER probability</div></div>',
                unsafe_allow_html=True
            )
        else:
            ratio,R,M,score = demo_predict(model_name,ab40,ab42,age,sex)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={"suffix":"/100","font":{"size":52,"color":"#0B2F5B"}},
                title={"text":"Illustrative software output"},
                gauge={"axis":{"range":[0,100]},"bar":{"color":"#1666A8","thickness":.2},"steps":[{"range":[0,100],"color":"#EDF5FA"}]}
            ))
            fig.update_layout(height=325,margin=dict(l=20,r=20,t=45,b=5),paper_bgcolor="white")
            st.plotly_chart(fig,use_container_width=True)
            st.markdown('<div class="danger"><b>NOT A CLINICALLY DERIVED AMBER SCORE.</b><br>Placeholder coefficients are used only to demonstrate the software interface.</div>',unsafe_allow_html=True)

            report = {
                "application":APP_VERSION,
                "generated_at":datetime.now().isoformat(timespec="minutes"),
                "model_configuration":model_name,
                "inputs":{"ab40_pg_ml":ab40,"ab42_pg_ml":ab42},
                "derived":{"ratio":ratio,"R":R,"M":M},
                "illustrative_score":score,
                "warning":"Demonstration only; not clinically validated."
            }
            st.download_button(
                "Download prototype research report (.json)",
                data=json.dumps(report,indent=2),
                file_name="AMBER_V01_demo_report.json",
                mime="application/json",
                use_container_width=True
            )

    with right:
        st.markdown("### 3. Scientific transparency")
        st.markdown('<div class="eqpanel">',unsafe_allow_html=True)
        st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
        st.markdown("**AMBER-B**")
        st.latex(r"I_B=\beta_0+\beta_RR+\beta_MM")
        st.markdown("**AMBER-C**")
        st.latex(r"I_C=\beta_0+\beta_RR+\beta_MM+\beta_A Age+\beta_S Sex")
        st.latex(r"P=\frac{1}{1+e^{-I}}")
        st.markdown('</div>',unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="info"><b>Important:</b> R and M do not create new information; they are an interpretable re-parameterization of the two log-transformed biomarker concentrations.</div>',unsafe_allow_html=True)

elif nav == "DNA Compass / Method":
    hero(
        "DNA Compass / Method",
        "This page explains the molecular-to-computational architecture at a scientific level while deliberately excluding unpublished DNA sequences, geometry, fabrication parameters, and other patent-sensitive implementation details.",
        "NANOTECHNOLOGY LAYER",
        ["Dual biomarker recognition","Quantitative readout","Aβ40 + Aβ42","Internal transformation","AMBER integration"],
    )

    cols = st.columns(5)
    for col,(n,h,t) in zip(cols,[
        ("1","Sample","Plasma input"),
        ("2","DNA Compass","Programmable dual recognition"),
        ("3","Readout","Quantitative Aβ40 + Aβ42"),
        ("4","Transform","Ratio, R and M"),
        ("5","Inference","Future PET-trained AMBER model"),
    ]):
        with col:
            st.markdown(card(n,h,t),unsafe_allow_html=True)

    st.write("")
    l,r = st.columns(2,gap="large")
    with l:
        st.markdown("### Why measure both peptides?")
        st.write(
            "The scientific objective is not simply to reproduce a known ratio. "
            "The project tests whether preserving the two measured concentrations "
            "provides reproducible information beyond a ratio-only representation."
        )
        st.markdown('<div class="info"><b>Meaningful comparison:</b> ratio-only versus the joint two-biomarker model. R and M are simply an interpretable coordinate system for that joint information.</div>',unsafe_allow_html=True)
    with r:
        st.markdown("### Contemporary comparator")
        st.write(
            "p-tau217 should be treated as a contemporary comparator where available. "
            "AMBER does not need to claim that Aβ42/Aβ40 is universally superior to p-tau217."
        )
        st.markdown('<div class="notice"><b>Public disclosure boundary:</b> keep exact DNA architecture and experimental implementation details outside the public app until patent filing.</div>',unsafe_allow_html=True)

elif nav == "Model & Validation":
    hero(
        "Model & Validation",
        "This page defines in advance how AMBER will be evaluated when real PET-linked hospital data become available. It is a research protocol interface, not a results page.",
        "EVIDENCE FRAMEWORK",
        ["Prespecified models","Bootstrap validation","Calibration","Decision curve","External validation"],
    )

    st.markdown('<div class="section-title">Prespecified comparisons</div>',unsafe_allow_html=True)
    df = pd.DataFrame([
        ["Aβ40 alone","Single-biomarker comparator"],
        ["Aβ42 alone","Single-biomarker comparator"],
        ["Aβ42/Aβ40 ratio","Conventional ratio comparator"],
        ["AMBER-B: R + M","Primary joint biomarker model"],
        ["AMBER-C: R + M + age + sex","Clinical extension if incremental value is reproducible"],
        ["p-tau217","Optional contemporary comparator"],
        ["p-tau217/Aβ42","Optional contemporary ratio comparator"],
    ], columns=["Model / biomarker","Purpose"])
    st.dataframe(df,hide_index=True,use_container_width=True)

    st.write("")
    a,b,c = st.columns(3,gap="large")
    with a:
        st.markdown(card("A","Discrimination","AUROC with confidence intervals and paired model comparison where appropriate."),unsafe_allow_html=True)
    with b:
        st.markdown(card("B","Calibration","Calibration intercept, slope, plot, and Brier score."),unsafe_allow_html=True)
    with c:
        st.markdown(card("C","Clinical utility","Decision-curve analysis plus prespecified rule-out and rule-in operating targets."),unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-title">Future validation outputs</div>',unsafe_allow_html=True)
    p1,p2,p3 = st.columns(3,gap="large")
    with p1:
        st.markdown('<div class="placeholder"><div><b>ROC / AUROC</b><br>Awaiting real PET-linked data</div></div>',unsafe_allow_html=True)
    with p2:
        st.markdown('<div class="placeholder"><div><b>Calibration</b><br>Awaiting model derivation and validation</div></div>',unsafe_allow_html=True)
    with p3:
        st.markdown('<div class="placeholder"><div><b>Decision curve</b><br>Awaiting clinically defined thresholds</div></div>',unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="info"><b>Model-lock rule:</b> preprocessing, coefficients, calibration, and thresholds are frozen before external validation. Any later recalibration becomes a new model version.</div>',unsafe_allow_html=True)

else:
    hero(
        "About AMBER",
        "AMBER is a research architecture linking nanoscale dual-amyloid measurement with transparent probabilistic inference of cerebral amyloid pathology. The present V0.1 focuses on scientific clarity rather than clinical software complexity.",
        "SCIENTIFIC INFORMATION",
        ["Research use only","No diagnostic claim","Patent next","Hospital validation later"],
    )

    a,b,c = st.columns(3,gap="large")
    with a:
        st.markdown(card("01","What AMBER is","A research platform for integrating DNA Compass measurements, biomarker representation, future model validation, and reproducible scientific reporting."),unsafe_allow_html=True)
    with b:
        st.markdown(card("02","What AMBER is not","Not currently an Alzheimer's disease diagnosis, a stand-alone diagnostic test, or a substitute for PET, CSF testing, or clinical assessment."),unsafe_allow_html=True)
    with c:
        st.markdown(card("03","Current stage","Frontend research prototype complete. Patent preparation is next; hospital data and formal model validation follow later."),unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-title">Development path</div>',unsafe_allow_html=True)
    cols = st.columns(5)
    for col,(n,h,t) in zip(cols,[
        ("1","Frontend","Research prototype"),
        ("2","Patent","Protect invention"),
        ("3","Hospital data","Aβ40/Aβ42 + PET"),
        ("4","Validation","Colab scientific pipeline"),
        ("5","Validated app","Locked model integration"),
    ]):
        with col:
            st.markdown(card(n,h,t),unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="notice"><b>IP note:</b> potentially novel DNA Compass engineering details should remain outside the public application until institutional patent filing is complete.</div>',unsafe_allow_html=True)

st.markdown(
    f'<div class="footer"><div><b>{APP_VERSION}</b></div><div>Model status: {MODEL_STATUS}</div><div>Research use only · Not a diagnostic test</div></div>',
    unsafe_allow_html=True
)
