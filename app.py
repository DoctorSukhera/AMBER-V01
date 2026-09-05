import base64
import json
import math
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="AMBER Score Platform", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

APP_VERSION = "AMBER V0.1"
MODEL_STATUS = "DEMONSTRATION ONLY"
DEMO_B = {"intercept": -1.40, "R": -1.00, "M": 0.18}
DEMO_C = {"intercept": -1.70, "R": -1.10, "M": 0.20, "age": 0.012, "sex": 0.15}

if "amber_result" not in st.session_state:
    st.session_state.amber_result = None
if "amber_report" not in st.session_state:
    st.session_state.amber_report = None

try:
    with open("assets/hitsz_logo.png", "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode("ascii")
except Exception:
    LOGO_B64 = ""

st.markdown("""
<style>
:root{--navy:#06285F;--navy2:#0B3D8A;--gold:#F4B42D;--blue:#1768B2;--ink:#162741;--muted:#65778E;--line:#CFE0F2;--warn:#FFF8E6;--danger:#FFF0F0}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.stApp{background:#fff;color:var(--ink)}
.block-container{max-width:1520px;padding-top:3.7rem!important;padding-bottom:2rem}
header[data-testid="stHeader"]{background:rgba(255,255,255,.96);border-bottom:1px solid #EDF2F7}
.hero{position:relative;overflow:hidden;background:linear-gradient(105deg,#041C45 0%,#06285F 58%,#0B3D8A 100%);color:#fff;border-radius:0 0 24px 24px;padding:22px 28px 24px;margin:-1rem 0 1rem;box-shadow:0 14px 30px rgba(5,40,95,.12)}
.hero:after{content:"";position:absolute;right:-35px;top:-70px;width:500px;height:235px;border-radius:50%;background:radial-gradient(circle at 42% 48%,rgba(255,196,78,.32) 0 4%,transparent 5%),radial-gradient(circle at 60% 43%,rgba(255,196,78,.24) 0 4%,transparent 5%),radial-gradient(circle at 53% 52%,rgba(165,208,255,.22) 0 28%,rgba(86,149,220,.12) 29% 40%,transparent 41%)}
.hero:before{content:"DNA   •   AI   •   BRAIN";position:absolute;right:34px;bottom:18px;color:rgba(255,255,255,.42);letter-spacing:.22em;font-size:.7rem;font-weight:700}
.hero-brand{position:relative;z-index:2;display:flex;align-items:center;gap:18px}.hero-logo{width:68px;height:68px;object-fit:contain;filter:brightness(0) invert(1);opacity:.98}.hero-title{font-size:2.35rem;line-height:1;font-weight:850;letter-spacing:-.035em}.hero-title .amber{color:var(--gold)}.hero-sub{margin-top:.4rem;color:#E9EFF8;font-size:.98rem}.badges{position:relative;z-index:2;display:flex;gap:.42rem;flex-wrap:wrap;margin-top:.75rem}.badge{padding:.29rem .62rem;border-radius:999px;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.15);font-size:.68rem;font-weight:760;color:#fff}
div[data-testid="stSegmentedControl"]{margin-bottom:1rem}div[data-testid="stSegmentedControl"] button{border-radius:7px!important;font-weight:750!important;min-height:42px!important}div[data-testid="stSegmentedControl"] button[aria-checked="true"]{background:#FFF6E0!important;border-color:#F2B93E!important;color:#9A6200!important}
.kicker{color:var(--navy2);font-size:.72rem;font-weight:850;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.2rem}.page-title{color:var(--navy);font-size:2rem;font-weight:850;letter-spacing:-.025em;margin-bottom:.18rem}.page-sub{color:#61758B;font-size:1rem;margin-bottom:1rem}.section-title{color:var(--navy);font-size:1.35rem;font-weight:850;margin:1.05rem 0 .65rem}
.panel{border:1px solid var(--line);border-radius:16px;background:#fff;padding:18px;box-shadow:0 6px 18px rgba(27,75,118,.045);height:100%}.soft{border:1px solid #C7DCF2;border-radius:15px;padding:16px;background:linear-gradient(180deg,#FCFEFF,#F2F8FE)}.notice{border:1px solid #E8CE89;border-radius:12px;background:#FFF8E6;color:#6A5317;padding:11px 14px}.danger{border:1px solid #EFC5C5;border-radius:12px;background:#FFF0F0;color:#9B3232;padding:11px 14px}
.info-bar{display:flex;gap:16px;align-items:center;border:1px solid #C7DCF2;background:linear-gradient(90deg,#F7FBFF,#EEF6FF);border-radius:15px;padding:18px}.info-icon{width:56px;height:56px;border-radius:50%;background:#0B3D8A;color:white;display:flex;align-items:center;justify-content:center;font-size:1.4rem;font-weight:900;box-shadow:inset 0 0 0 7px #E5F1FF}.info-title{color:var(--navy);font-weight:850;font-size:1.05rem}.info-body{color:#33557E;line-height:1.5;margin-top:.2rem}
.icon-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.icon-card{border:1px solid var(--line);border-radius:16px;padding:18px;background:#fff;display:flex;gap:16px;align-items:center}.icon-bubble{width:60px;height:60px;border-radius:50%;background:#E8F3FF;border:1px solid #C9DDF4;color:#0B59B0;display:flex;align-items:center;justify-content:center;font-size:1.55rem;flex:0 0 auto}.icon-bubble.gold{background:#FFF2D2;border-color:#F3D78F;color:#C78300}.icon-title{color:var(--navy);font-weight:850;margin-bottom:.25rem}.icon-body{color:#5D7187;font-size:.9rem;line-height:1.45}
.flow{display:flex;gap:12px;align-items:stretch;flex-wrap:wrap}.flow-card{flex:1 1 155px;min-width:150px;border:1px solid var(--line);border-radius:16px;padding:15px;background:#fff;text-align:center;position:relative}.flow-num{position:absolute;left:12px;top:12px;width:30px;height:30px;border-radius:50%;background:#E8F3FF;color:#0B3D8A;display:flex;align-items:center;justify-content:center;font-weight:850}.flow-icon{width:54px;height:54px;border-radius:50%;background:#EEF6FF;color:#0B59B0;display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin:0 auto .55rem}.flow-title{color:var(--navy);font-weight:850;margin-bottom:.25rem}.flow-body{color:#607489;font-size:.86rem;line-height:1.43}.arrow{align-self:center;color:#7F9ABA;font-size:1.3rem;font-weight:850}
.calc-wrap{border:1px solid var(--line);border-radius:18px;padding:16px;background:#fff;box-shadow:0 6px 18px rgba(27,75,118,.035)}.calc-head{display:flex;align-items:center;gap:10px;margin-bottom:8px}.step-badge{width:38px;height:38px;border-radius:50%;background:#E4F0FF;color:#0B3D8A;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:1.1rem}.calc-title{color:var(--navy);font-size:1.28rem;font-weight:850}.placeholder{min-height:250px;border:1px dashed #AFC4DC;border-radius:16px;background:#FAFCFF;display:flex;align-items:center;justify-content:center;text-align:center;color:#6C7E93;padding:20px}.metric-row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}.metric-card{border:1px solid var(--line);border-radius:12px;background:#fff;padding:10px;text-align:center}.metric-name{color:#7A8DA3;font-size:.69rem;font-weight:750}.metric-value{color:var(--navy);font-size:1.35rem;font-weight:850}.eqbox{border:1px solid var(--line);border-radius:14px;background:#FBFDFF;padding:14px}.safeguard{border:1px solid #F0D7A1;border-radius:12px;background:#FFF8E8;padding:12px;color:#6B5520}
.mol-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}.mol-card{border:1px solid var(--line);border-radius:16px;background:#fff;padding:16px;text-align:center}.mol-icon{width:62px;height:62px;border-radius:50%;background:#EDF6FF;color:#1263BB;display:flex;align-items:center;justify-content:center;font-size:1.6rem;margin:0 auto .6rem}.mol-title{color:var(--navy);font-weight:850}.mol-body{color:#63768A;font-size:.84rem;line-height:1.42;margin-top:.25rem}
.validation-card{border:1px solid var(--line);border-radius:16px;background:#fff;padding:15px}.val-title{display:flex;align-items:center;gap:10px;color:var(--navy);font-weight:850;font-size:1.05rem;margin-bottom:.35rem}.val-icon{width:38px;height:38px;border-radius:50%;background:#E8F3FF;color:#0B59B0;display:flex;align-items:center;justify-content:center}.val-sub{color:#607489;font-size:.84rem;margin-bottom:.25rem}
.timeline{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}.tstep{border:1px solid var(--line);border-radius:16px;background:#fff;padding:16px;text-align:center}.tnum{width:30px;height:30px;border-radius:50%;background:#E8F3FF;color:#0B3D8A;display:flex;align-items:center;justify-content:center;font-weight:850}.ticon{font-size:1.55rem;color:#0B59B0;margin:.25rem 0 .35rem}.ttitle{color:var(--navy);font-weight:850}.tbody{color:#617489;font-size:.84rem;line-height:1.43;margin-top:.25rem}.tstatus{display:inline-block;margin-top:.7rem;padding:.22rem .55rem;border-radius:999px;background:#EDF4FD;color:#0B59B0;font-size:.7rem;font-weight:750}.tstatus.current{background:#FFF0C7;color:#865B00}
.stButton>button,.stFormSubmitButton>button{background:linear-gradient(90deg,#06285F,#0B3D8A);color:#fff;border:none;border-radius:10px;font-weight:850;min-height:46px}.stDownloadButton>button{background:#fff;color:var(--navy);border:1px solid #BDD2E9;border-radius:10px;font-weight:750}h1,h2,h3,h4{color:var(--navy)!important}.footer{border-top:1px solid var(--line);margin-top:1.25rem;padding-top:.75rem;color:#7D8D9E;font-size:.73rem;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
@media(max-width:980px){.icon-grid{grid-template-columns:1fr}.mol-grid{grid-template-columns:1fr 1fr}.timeline{grid-template-columns:1fr 1fr}}
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
        I = c["intercept"] + c["R"]*R + c["M"]*M + c["age"]*age + c["sex"]*(1 if sex == "Female" else 0)
    return ratio, R, M, sigmoid(I)*100

logo_html = f'<img class="hero-logo" src="data:image/png;base64,{LOGO_B64}" alt="HIT Shenzhen">' if LOGO_B64 else '<div style="width:62px;height:62px;border:2px solid #F4B42D;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#F4B42D;font-weight:900">HIT</div>'

st.markdown(f'''<div class="hero"><div class="hero-brand">{logo_html}<div><div class="hero-title"><span class="amber">AMBER</span> Score Platform</div><div class="hero-sub">Blood-based molecular research platform for estimation of cerebral amyloid positivity.</div></div></div><div class="badges"><span class="badge">V0.1 · RESEARCH PROTOTYPE</span><span class="badge">DNA COMPASS + COMPUTATIONAL INFERENCE</span><span class="badge">NO CLINICAL VALIDATION CLAIMS</span></div></div>''', unsafe_allow_html=True)

pages = ["Home","AMBER Calculator","DNA Compass / Method","Model & Validation","About AMBER"]
page = st.segmented_control("Navigation", pages, default="Home", label_visibility="collapsed") or "Home"

if page == "Home":
    st.markdown('<div class="kicker">Research concept</div><div class="page-title">Why AMBER, and how does it work?</div><div class="page-sub">From blood-based molecular measurement to a future estimate of cerebral amyloid positivity.</div>', unsafe_allow_html=True)
    st.markdown('''<div class="info-bar"><div class="info-icon">?</div><div><div class="info-title">MAIN SCIENTIFIC QUESTION</div><div class="info-body">Can simultaneous blood-based measurement of Aβ40 and Aβ42, enabled by a programmable DNA Compass assay, support a transparent and eventually validated estimate of PET-defined cerebral amyloid positivity?</div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Why this project matters</div>', unsafe_allow_html=True)
    st.markdown('''<div class="icon-grid"><div class="icon-card"><div class="icon-bubble">🧠</div><div><div class="icon-title">Imaging-defined pathology</div><div class="icon-body">Amyloid PET can define cerebral amyloid pathology.</div></div></div><div class="icon-card"><div class="icon-bubble gold">🧪</div><div><div class="icon-title">Two related biomarkers</div><div class="icon-body">Aβ40 and Aβ42 are highly related peptides that must be quantified robustly.</div></div></div><div class="icon-card"><div class="icon-bubble">📊</div><div><div class="icon-title">Translation gap</div><div class="icon-body">Molecular measurements become useful only when linked to transparent, calibrated and externally validated pathology estimates.</div></div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">AMBER research pathway</div>', unsafe_allow_html=True)
    st.markdown('''<div class="flow"><div class="flow-card"><div class="flow-num">1</div><div class="flow-icon">🩸</div><div class="flow-title">Measure</div><div class="flow-body">Quantify plasma Aβ40 and Aβ42 using the DNA Compass workflow.</div></div><div class="arrow">→</div><div class="flow-card"><div class="flow-num">2</div><div class="flow-icon">🧬</div><div class="flow-title">Transform</div><div class="flow-body">Derive Aβ42/Aβ40 and interpretable R and M features.</div></div><div class="arrow">→</div><div class="flow-card"><div class="flow-num">3</div><div class="flow-icon">💻</div><div class="flow-title">Model</div><div class="flow-body">Compare ratio-only, AMBER-B and AMBER-C models.</div></div><div class="arrow">→</div><div class="flow-card"><div class="flow-num">4</div><div class="flow-icon">🛡️</div><div class="flow-title">Validate</div><div class="flow-body">Use PET-linked hospital data for discrimination, calibration and utility analysis.</div></div><div class="arrow">→</div><div class="flow-card"><div class="flow-num">5</div><div class="flow-icon">👥</div><div class="flow-title">Translate</div><div class="flow-body">Load only a locked validated model into the future AMBER interface.</div></div></div>''', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="notice"><b>Current stage:</b> AMBER V0.1 demonstrates the scientific and software architecture only. Clinical coefficients, thresholds and performance claims will be added only after real PET-linked data are analyzed.</div>', unsafe_allow_html=True)

elif page == "AMBER Calculator":
    st.markdown('<div class="kicker">Core computational interface</div><div class="page-title">AMBER Calculator</div><div class="page-sub">Manual calculation only — results appear after you click Calculate AMBER Score.</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1.03,1], gap="large")
    with c1:
        st.markdown('<div class="calc-wrap"><div class="calc-head"><div class="step-badge">1</div><div><div class="calc-title">Input values</div><div style="color:#667A91;font-size:.85rem">Enter biomarker values and, for AMBER-C, demographic variables.</div></div></div>', unsafe_allow_html=True)
        with st.form("amber_form"):
            model_name = st.selectbox("Model configuration", ["AMBER-B (biomarker-only)","AMBER-C (biomarker + age/sex)"])
            amber_b = model_name.startswith("AMBER-B")
            if not amber_b:
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
        st.markdown('<div class="soft" style="margin-top:10px"><b style="color:#0B3D8A">ⓘ</b> The calculation is performed only after you click “Calculate AMBER Score”.</div></div>', unsafe_allow_html=True)
        if submitted:
            ratio,R,M = derive(ab40,ab42)
            score = None
            if demo:
                ratio,R,M,score = demo_predict(model_name,ab40,ab42,age,sex)
            st.session_state.amber_result = {"model":model_name,"ratio":ratio,"R":R,"M":M,"score":score,"demo":demo}
            st.session_state.amber_report = {"application":APP_VERSION,"generated_at":datetime.now().isoformat(timespec="minutes"),"configuration":model_name,"inputs":{"ab40_pg_ml":ab40,"ab42_pg_ml":ab42,"age":None if amber_b else age,"sex":None if amber_b else sex},"derived":{"ratio":ratio,"R":R,"M":M},"illustrative_score":score,"status":"DEMONSTRATION ONLY" if demo else "DERIVED FEATURES ONLY"}
    with c2:
        st.markdown('<div class="calc-wrap"><div class="calc-head"><div class="step-badge">2</div><div><div class="calc-title">Results</div><div style="color:#667A91;font-size:.85rem">Illustrative output based on the current inputs.</div></div></div>', unsafe_allow_html=True)
        r = st.session_state.amber_result
        if r is None:
            st.markdown('<div class="placeholder"><div>Enter values on the left and click<br><b style="color:#06285F">CALCULATE AMBER SCORE</b>.</div></div>', unsafe_allow_html=True)
        else:
            if r["demo"]:
                fig = go.Figure(go.Indicator(mode="gauge+number", value=r["score"], number={"suffix":"/100","font":{"size":55,"color":"#06285F"}}, title={"text":"Illustrative AMBER software output","font":{"size":14,"color":"#6A7D92"}}, gauge={"shape":"angular","axis":{"range":[0,100],"tickvals":[0,50,100]},"bar":{"color":"#0B3D8A","thickness":.18},"bgcolor":"#EFF4FA","borderwidth":0}))
                fig.update_layout(height=285,margin=dict(l=20,r=20,t=35,b=0),paper_bgcolor="white")
                st.plotly_chart(fig,use_container_width=True)
            else:
                st.markdown('<div class="placeholder"><div><b style="color:#06285F">Derived biomarker features calculated.</b><br><br>No validated probability model is loaded.</div></div>', unsafe_allow_html=True)
            st.markdown(f'''<div class="metric-row"><div class="metric-card"><div class="metric-name">Aβ42/Aβ40</div><div class="metric-value">{r["ratio"]:.4f}</div></div><div class="metric-card"><div class="metric-name">R</div><div class="metric-value">{r["R"]:.3f}</div></div><div class="metric-card"><div class="metric-name">M</div><div class="metric-value">{r["M"]:.3f}</div></div></div>''', unsafe_allow_html=True)
            if r["demo"]:
                st.markdown('<div class="danger" style="margin-top:10px"><b>⚠ DEMONSTRATION OUTPUT ONLY.</b><br>Placeholder coefficients are used only to demonstrate the interface. This is not a clinically validated AMBER result.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.amber_report is not None:
            st.write("")
            st.download_button("Download results summary (.json)", json.dumps(st.session_state.amber_report,indent=2), "AMBER_V01_results.json", "application/json", use_container_width=True)
    with c3:
        st.markdown('<div class="calc-wrap"><div class="calc-head"><div class="step-badge">3</div><div><div class="calc-title">Scientific basis</div><div style="color:#667A91;font-size:.85rem">Transparent feature definitions and model structure.</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="eqbox">', unsafe_allow_html=True)
        st.markdown("**Feature definitions**")
        st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
        st.markdown("**AMBER-B (biomarker-only)**")
        st.latex(r"I_B=\beta_0+\beta_RR+\beta_MM")
        st.markdown("**AMBER-C (with demographics)**")
        st.latex(r"I_C=\beta_0+\beta_RR+\beta_MM+\beta_AAge+\beta_SSex")
        st.markdown("**Probability (both models)**")
        st.latex(r"P=\frac{1}{1+e^{-I}}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="safeguard" style="margin-top:10px"><b>💡 Scientific safeguard:</b> no final β coefficients, clinical thresholds, AUC, sensitivity, specificity or model-lock date are shown until empirically derived and validated.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">What happens after you click Calculate?</div>', unsafe_allow_html=True)
    st.markdown('''<div class="flow"><div class="flow-card"><div class="flow-num">1</div><div class="flow-icon">📋</div><div class="flow-title">Read inputs</div><div class="flow-body">Get biomarker and demographic values.</div></div><div class="arrow">→</div><div class="flow-card"><div class="flow-num">2</div><div class="flow-icon">⚙️</div><div class="flow-title">Derive features</div><div class="flow-body">Compute ratio, R and M.</div></div><div class="arrow">→</div><div class="flow-card"><div class="flow-num">3</div><div class="flow-icon">📊</div><div class="flow-title">Apply model</div><div class="flow-body">A future locked model converts features into a calibrated probability.</div></div><div class="arrow">→</div><div class="flow-card"><div class="flow-num">4</div><div class="flow-icon">📄</div><div class="flow-title">Report</div><div class="flow-body">Display output and export a reproducible research summary.</div></div></div>''', unsafe_allow_html=True)

elif page == "DNA Compass / Method":
    st.markdown('<div class="kicker">Nanotechnology layer</div><div class="page-title">Integrated molecular workflow</div><div class="page-sub">From blood-derived sample to a PET-informed estimate of cerebral amyloid positivity.</div>', unsafe_allow_html=True)
    st.markdown('''<div class="info-bar"><div class="info-icon">i</div><div><div class="info-title">Purpose of this page</div><div class="info-body">To show the molecular-to-computational architecture directly in the web interface, while keeping unpublished sequences, precise geometry, fabrication parameters and other patent-sensitive implementation details outside the public app.</div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">DNA Compass → AMBER</div>', unsafe_allow_html=True)
    st.markdown('''<div class="mol-grid"><div class="mol-card"><div class="mol-icon">🩸</div><div class="mol-title">Plasma</div><div class="mol-body">Blood-derived research sample.</div></div><div class="mol-card"><div class="mol-icon">🧬</div><div class="mol-title">DNA Compass</div><div class="mol-body">Programmable molecular recognition architecture.</div></div><div class="mol-card"><div class="mol-icon">🔗</div><div class="mol-title">Aβ40 + Aβ42</div><div class="mol-body">Simultaneous selective acquisition of the two amyloid peptides.</div></div><div class="mol-card"><div class="mol-icon">☀️</div><div class="mol-title">Optical readout</div><div class="mol-body">Quantitative reporter signal converted into concentrations.</div></div><div class="mol-card"><div class="mol-icon">💻</div><div class="mol-title">Transform</div><div class="mol-body">Ratio, R and M are derived computationally.</div></div><div class="mol-card"><div class="mol-icon">🧠</div><div class="mol-title">AMBER</div><div class="mol-body">Future PET-trained model estimates cerebral amyloid positivity.</div></div></div>''', unsafe_allow_html=True)
    st.write("")
    l,r = st.columns(2,gap="large")
    with l:
        st.markdown('<div class="panel"><div class="icon-card" style="border:none;padding:0"><div class="icon-bubble">🧠</div><div><div class="icon-title">Why Aβ40 and Aβ42?</div><div class="icon-body">This project focuses on the direct amyloid molecular pair because the reference endpoint is cerebral amyloid deposition. The modelling question is whether retaining both measured dimensions adds reproducible value beyond the ratio alone.</div></div></div></div>', unsafe_allow_html=True)
    with r:
        st.markdown('<div class="panel"><div class="icon-card" style="border:none;padding:0"><div class="icon-bubble">📊</div><div><div class="icon-title">Contemporary comparator</div><div class="icon-body">p-tau217 can be included as a contemporary comparator where available. AMBER examines added value transparently rather than claiming universal superiority.</div></div></div></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="notice"><b>📣 Public-disclosure boundary:</b> exact DNA sequences, architecture dimensions, fabrication parameters, recognition chemistry and other potentially novel implementation details are intentionally not displayed here.</div>', unsafe_allow_html=True)

elif page == "Model & Validation":
    st.markdown('<div class="kicker">Evidence framework</div><div class="page-title">Future validation dashboard</div><div class="page-sub">Real dashboard components are shown in an empty state until PET-linked validation data are available.</div>', unsafe_allow_html=True)
    st.markdown('<div class="notice"><b>📣 No performance metrics are claimed in V0.1.</b> The panels below are placeholders for future real-data outputs.</div>', unsafe_allow_html=True)
    v1,v2,v3 = st.columns(3,gap="large")
    with v1:
        st.markdown('<div class="validation-card"><div class="val-title"><div class="val-icon">📈</div>ROC / AUROC</div><div class="val-sub">Discrimination ability to identify cerebral amyloid positivity.</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines", line=dict(dash="dash",color="#8FB1D6"), showlegend=False))
        fig.update_layout(height=320,margin=dict(l=45,r=20,t=20,b=45),paper_bgcolor="white",plot_bgcolor="#FBFDFF",xaxis_title="1 − Specificity",yaxis_title="Sensitivity",xaxis=dict(range=[0,1]),yaxis=dict(range=[0,1]),annotations=[dict(x=.5,y=.58,xref="paper",yref="paper",text="<b>Awaiting PET-linked hospital data</b><br>No AUROC is calculated in V0.1",showarrow=False,font=dict(color="#6A7C90",size=13))])
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with v2:
        st.markdown('<div class="validation-card"><div class="val-title"><div class="val-icon">🎯</div>Calibration</div><div class="val-sub">Agreement between predicted and observed probability.</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines", line=dict(dash="dash",color="#8FB1D6"), showlegend=False))
        fig.update_layout(height=320,margin=dict(l=45,r=20,t=20,b=45),paper_bgcolor="white",plot_bgcolor="#FBFDFF",xaxis_title="Predicted probability",yaxis_title="Observed probability",xaxis=dict(range=[0,1]),yaxis=dict(range=[0,1]),annotations=[dict(x=.5,y=.58,xref="paper",yref="paper",text="<b>Awaiting model derivation</b><br>Intercept · slope · plot · Brier score",showarrow=False,font=dict(color="#6A7C90",size=13))])
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with v3:
        st.markdown('<div class="validation-card"><div class="val-title"><div class="val-icon">📊</div>Decision-curve analysis</div><div class="val-sub">Clinical net benefit across threshold probabilities.</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_hline(y=0,line_dash="dash",line_color="#8FB1D6")
        fig.update_layout(height=320,margin=dict(l=45,r=20,t=20,b=45),paper_bgcolor="white",plot_bgcolor="#FBFDFF",xaxis_title="Threshold probability",yaxis_title="Net benefit",xaxis=dict(range=[0,1]),yaxis=dict(range=[-.1,.4]),annotations=[dict(x=.5,y=.58,xref="paper",yref="paper",text="<b>Awaiting prespecified operating thresholds</b><br>No net-benefit curve is calculated in V0.1",showarrow=False,font=dict(color="#6A7C90",size=13))])
        st.plotly_chart(fig,use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Prespecified model comparison</div>', unsafe_allow_html=True)
    df = pd.DataFrame([["Aβ40 alone","Single-biomarker comparator"],["Aβ42 alone","Single-biomarker comparator"],["Aβ42/Aβ40 ratio","Conventional ratio comparator"],["AMBER-B (R + M)","Primary joint biomarker model"],["AMBER-C (R + M + age + sex)","Clinical extension if incremental value is reproducible"],["p-tau217","Optional contemporary comparator"],["p-tau217/Aβ42","Optional comparator"]],columns=["Model / biomarker","Purpose"])
    st.dataframe(df,hide_index=True,use_container_width=True)
    st.write("")
    st.markdown('<div class="soft"><b style="color:#0B3D8A">🔒 Model-lock principle:</b> preprocessing, coefficients, calibration and operating thresholds must be frozen before independent external validation. Any later recalibration becomes a new model version.</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="kicker">Scientific information</div><div class="page-title">About AMBER</div>', unsafe_allow_html=True)
    st.markdown('''<div class="info-bar"><div class="info-icon">i</div><div><div class="info-title">AMBER is a research architecture, not yet a clinical diagnostic product.</div><div class="info-body">Its purpose is to integrate DNA Compass molecular measurement with transparent computational modelling and later PET-linked validation in a reproducible research platform.</div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Development sequence</div>', unsafe_allow_html=True)
    st.markdown('''<div class="timeline"><div class="tstep"><div class="tnum">1</div><div class="ticon">💻</div><div class="ttitle">App</div><div class="tbody">Finalize the research-oriented user interface and computational architecture.</div><span class="tstatus current">Current</span></div><div class="tstep"><div class="tnum">2</div><div class="ticon">📄</div><div class="ttitle">Patent</div><div class="tbody">Define the protectable DNA Compass + AMBER technical architecture and prepare filing documents.</div><span class="tstatus">Next</span></div><div class="tstep"><div class="tnum">3</div><div class="ticon">🏥</div><div class="ttitle">Hospital data</div><div class="tbody">Obtain paired Aβ40, Aβ42 and amyloid PET outcome data under the approved study design.</div><span class="tstatus">Future</span></div><div class="tstep"><div class="tnum">4</div><div class="ticon">📊</div><div class="ttitle">Validation</div><div class="tbody">Use the Colab scientific pipeline for derivation, bootstrap validation, calibration and external validation.</div><span class="tstatus">Future</span></div><div class="tstep"><div class="tnum">5</div><div class="ticon">☁️</div><div class="ttitle">Update</div><div class="tbody">Load the frozen validated model artifact into AMBER and release the new version.</div><span class="tstatus">After evidence</span></div></div>''', unsafe_allow_html=True)
    st.write("")
    a,b = st.columns(2,gap="large")
    with a:
        st.markdown('<div class="panel"><div class="icon-card" style="border:none;padding:0"><div class="icon-bubble">👥</div><div><div class="icon-title" style="font-size:1.12rem">Project</div><div class="icon-body"><b>A Project by</b><br>Fahim ElKassim<br><br><b>Supervised by</b><br>Prof. Xingyi Ma<br>NanoMax Group, HIT Shenzhen</div></div></div></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><div class="icon-card" style="border:none;padding:0"><div class="icon-bubble">⚙️</div><div><div class="icon-title" style="font-size:1.12rem">Development</div><div class="icon-body"><b>Designed and Developed by</b><br>Doctor Sukhera（学睿）<br><br><b>Version</b><br>AMBER V0.1 · Research Prototype<br><br><b>Technology</b><br>Dual-biomarker computational inference using Aβ42/Aβ40-derived features (ratio, R, M) with staged PET-linked validation.</div></div></div></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="notice"><b>📣 IP note:</b> potentially novel DNA Compass engineering details should remain outside the public application until institutional patent filing is complete.</div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer"><div><b>{APP_VERSION}</b></div><div>Model status: {MODEL_STATUS}</div><div>Research use only · Not a diagnostic test</div></div>', unsafe_allow_html=True)
