import math
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="AMBER V0.1", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

APP_VERSION = "AMBER V0.1"
AB40_RANGE = (20.0, 2000.0)
AB42_RANGE = (2.0, 200.0)

# DEMONSTRATION COEFFICIENTS ONLY — NOT CLINICALLY DERIVED
DEMO_B = {"intercept": -1.40, "R": -1.00, "M": 0.18}
DEMO_C = {"intercept": -1.70, "R": -1.10, "M": 0.20, "age": 0.012, "sex": 0.15}

st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:.8rem;padding-bottom:2rem}
.amber-top{background:linear-gradient(105deg,#071D49,#0A2F69);border-radius:18px;padding:22px 28px;color:white;margin-bottom:14px;box-shadow:0 8px 24px rgba(7,29,73,.12)}
.brand{font-size:2.05rem;font-weight:800}.amber{color:#F5B82E}.sub{margin-top:.35rem;opacity:.92}
.badge{display:inline-block;margin-top:.7rem;padding:.34rem .72rem;border-radius:999px;background:#EDF3FF;color:#0A2F69;font-weight:800;font-size:.78rem}
.hero{border:1px solid #DDE6F5;border-radius:18px;padding:28px 30px;background:linear-gradient(120deg,#fff,#F3F7FF)}
.hero h1{font-size:2.45rem;line-height:1.12;color:#071D49;margin:.1rem 0 .75rem}.hero p{color:#35435E;line-height:1.6}
.card{border:1px solid #DDE6F5;border-radius:16px;padding:18px;background:white;height:100%;box-shadow:0 3px 12px rgba(20,63,150,.035)}
.icon{font-size:1.45rem;margin-bottom:.45rem}.ct{font-weight:800;color:#071D49}.cb{color:#4D5B73;line-height:1.5;font-size:.92rem}
.kicker{color:#123F96;font-weight:800;text-transform:uppercase;font-size:.76rem;letter-spacing:.06em}.title{font-size:1.55rem;font-weight:800;color:#071D49;margin:.2rem 0 .8rem}
.notice{border:1px solid #F0D99E;background:#FFF8E8;border-radius:14px;padding:14px 16px;color:#7A5610}
.info{border:1px solid #CFE0FF;background:#F1F6FF;border-radius:14px;padding:14px 16px;color:#123F96}
.danger{border:1px solid #F5C8C8;background:#FFF0F0;border-radius:14px;padding:14px 16px;color:#9E3030}
.metric{border:1px solid #DDE6F5;border-radius:14px;padding:14px;background:#fff;text-align:center}.mn{font-size:.78rem;color:#69758A;font-weight:700}.mv{font-size:1.55rem;color:#071D49;font-weight:800}
.placeholder{border:1px dashed #B8C7E6;border-radius:16px;padding:28px 20px;text-align:center;color:#667085;background:#FBFCFF;min-height:180px;display:flex;align-items:center;justify-content:center}
.footer{border-top:1px solid #DDE6F5;padding-top:13px;margin-top:22px;color:#7A8495;font-size:.78rem}
div[data-testid="stRadio"] > div {gap:.25rem}
</style>
""", unsafe_allow_html=True)

def derive(ab40, ab42):
    ratio = ab42/ab40
    R = math.log10(ratio)
    M = math.log10(math.sqrt(ab40*ab42))
    return ratio,R,M

def sigmoid(x):
    return 1/(1+math.exp(-x))

def predict_demo(model_name, ab40, ab42, age, sex):
    ratio,R,M = derive(ab40,ab42)
    if model_name.startswith("AMBER-B"):
        c=DEMO_B
        I=c["intercept"]+c["R"]*R+c["M"]*M
    else:
        c=DEMO_C
        I=c["intercept"]+c["R"]*R+c["M"]*M+c["age"]*age+c["sex"]*(1 if sex=="Female" else 0)
    p=sigmoid(I)
    return ratio,R,M,p*100

def card(icon,title,text):
    return f'<div class="card"><div class="icon">{icon}</div><div class="ct">{title}</div><div class="cb">{text}</div></div>'

st.markdown("""
<div class="amber-top">
<div class="brand">🧠 <span class="amber">AMBER</span> Score Platform</div>
<div class="sub">Blood-based research platform for estimation of cerebral amyloid positivity.</div>
<span class="badge">V0.1 · RESEARCH PROTOTYPE · DEMONSTRATION ONLY</span>
</div>
""", unsafe_allow_html=True)

pages=["Home","AMBER Calculator","DNA Compass / Method","Model & Validation","Longitudinal Monitoring","About / Scientific Information"]
page=st.radio("Navigation",pages,horizontal=True,label_visibility="collapsed")

if page=="Home":
    st.markdown("""
    <div class="hero">
      <div class="kicker">Molecular measurement → biological interpretation</div>
      <h1>From blood biomarkers to probability<br>of cerebral amyloid positivity</h1>
      <p>AMBER is being developed to connect simultaneous plasma Aβ40 and Aβ42 measurements with transparent computational inference of cerebral amyloid pathology. V0.1 demonstrates the software architecture only.</p>
    </div>""",unsafe_allow_html=True)
    st.write("")
    c1,c2,c3=st.columns(3,gap="large")
    with c1: st.markdown(card("🧪","1. Measure","Quantify plasma Aβ40 and Aβ42 using the DNA Compass analytical workflow."),unsafe_allow_html=True)
    with c2: st.markdown(card("ƒx","2. Transform","Derive the Aβ42/Aβ40 ratio and interpretable relative-composition and abundance terms."),unsafe_allow_html=True)
    with c3: st.markdown(card("📈","3. Estimate","Apply a future locked model to estimate individualized cerebral amyloid probability."),unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="title">How AMBER works</div>',unsafe_allow_html=True)
    cols=st.columns(6)
    steps=[("1","Sample","Plasma"),("2","DNA Compass","Dual acquisition"),("3","Aβ40 + Aβ42","Measured inputs"),("4","Transform","Ratio, R, M"),("5","Inference","AMBER-B / C"),("6","Output","Amyloid probability")]
    for col,(n,h,t) in zip(cols,steps):
        with col:
            st.markdown(f'<div class="card"><div class="ct">{n}. {h}</div><div class="cb">{t}</div></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="notice"><b>Important:</b> V0.1 contains no clinically derived coefficients or validated performance claims. It exists to test the workflow, usability, and software architecture.</div>',unsafe_allow_html=True)

elif page=="AMBER Calculator":
    st.markdown('<div class="kicker">Core workflow</div><div class="title">AMBER Calculator — V0.1 Prototype</div>',unsafe_allow_html=True)
    left,center,right=st.columns([.95,1.25,1],gap="large")
    with left:
        st.markdown("### 1. Input values")
        model=st.selectbox("Model configuration",["AMBER-B (biomarker-only demo)","AMBER-C (biomarker + age/sex demo)"],help="Scientific comparison configurations, not separate AMBER products.")
        ab40=st.number_input("Plasma Aβ40 (pg/mL)",min_value=.01,value=285.0,step=1.0,format="%.2f")
        st.caption("Prototype interface range: 20–2000 pg/mL")
        ab42=st.number_input("Plasma Aβ42 (pg/mL)",min_value=.01,value=18.5,step=.1,format="%.2f")
        st.caption("Prototype interface range: 2–200 pg/mL")
        age=st.number_input("Age (years)",18,100,68,disabled=model.startswith("AMBER-B"))
        sex=st.radio("Sex",["Male","Female"],horizontal=True,index=1,disabled=model.startswith("AMBER-B"))
        run=st.button("Calculate illustrative score",type="primary",use_container_width=True)
        st.caption("Aβ42/Aβ40, R and M are derived internally. Final coefficients do not yet exist.")
    with center:
        st.markdown("### 2. Illustrative result")
        if run:
            ratio,R,M,score=predict_demo(model,ab40,ab42,age,sex)
            if not AB40_RANGE[0]<=ab40<=AB40_RANGE[1]: st.warning("Aβ40 is outside the prototype interface range.")
            if not AB42_RANGE[0]<=ab42<=AB42_RANGE[1]: st.warning("Aβ42 is outside the prototype interface range.")
            fig=go.Figure(go.Indicator(mode="gauge+number",value=score,number={"suffix":"/100","font":{"size":52,"color":"#071D49"}},title={"text":"Illustrative software output"},gauge={"axis":{"range":[0,100]},"bar":{"color":"#0A2F69","thickness":.22},"steps":[{"range":[0,100],"color":"#EEF3FA"}]}))
            fig.update_layout(height=330,margin=dict(l=25,r=25,t=45,b=5),paper_bgcolor="white")
            st.plotly_chart(fig,use_container_width=True)
            st.markdown('<div class="danger"><b>ILLUSTRATIVE SOFTWARE OUTPUT — NOT A CLINICALLY DERIVED AMBER SCORE.</b><br>This number exists only to test the interface and calculation pathway.</div>',unsafe_allow_html=True)
            st.write("")
            a,b,c=st.columns(3)
            with a: st.markdown(f'<div class="metric"><div class="mn">Aβ42/Aβ40</div><div class="mv">{ratio:.4f}</div></div>',unsafe_allow_html=True)
            with b: st.markdown(f'<div class="metric"><div class="mn">R</div><div class="mv">{R:.3f}</div></div>',unsafe_allow_html=True)
            with c: st.markdown(f'<div class="metric"><div class="mn">M</div><div class="mv">{M:.3f}</div></div>',unsafe_allow_html=True)
            report=f"""AMBER V0.1 — RESEARCH PROTOTYPE
Generated: {datetime.now().isoformat(timespec='minutes')}
Model: {model}
Aβ40: {ab40:.2f} pg/mL
Aβ42: {ab42:.2f} pg/mL
Aβ42/Aβ40: {ratio:.6f}
R: {R:.6f}
M: {M:.6f}
Illustrative score: {score:.2f}/100

WARNING: demonstration coefficients only. Not clinically validated.
"""
            st.download_button("Download prototype summary (.txt)",report,"AMBER_V01_prototype_summary.txt","text/plain",use_container_width=True)
        else:
            st.markdown('<div class="placeholder"><div><b>No calculation yet</b><br>Enter values and click Calculate illustrative score.</div></div>',unsafe_allow_html=True)
    with right:
        st.markdown("### 3. Scientific transparency")
        st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
        st.markdown("**AMBER-B**")
        st.latex(r"I_B=\beta_0+\beta_RR+\beta_MM")
        st.markdown("**AMBER-C**")
        st.latex(r"I_C=\beta_0+\beta_RR+\beta_MM+\beta_AAge+\beta_SSex")
        st.latex(r"P=\frac{1}{1+e^{-I}}")
        st.markdown('<div class="notice"><b>Model status:</b> demonstration only. Final coefficients, calibration and thresholds must come from real outcome-labelled PET-linked data.</div>',unsafe_allow_html=True)

elif page=="DNA Compass / Method":
    st.markdown('<div class="kicker">Molecular acquisition architecture</div><div class="title">DNA Compass / Method</div>',unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1 style="font-size:2rem;">DNA Compass–enabled dual-biomarker measurement</h1><p>The intended AMBER architecture couples quantitative acquisition of plasma Aβ40 and Aβ42 to transparent computational interpretation. Experimental assay specifications will only be added after analytical validation and IP review.</p></div>',unsafe_allow_html=True)
    st.write("")
    cols=st.columns(6)
    for col,(ic,hd,tx) in zip(cols,[("🩸","Sample","Plasma"),("🧬","DNA Compass","Programmable recognition"),("🟣🔵","Aβ42 + Aβ40","Simultaneous capture"),("🔬","Readout","Quantification"),("ƒx","Transform","Ratio, R, M"),("🧠","AMBER","Probability")]):
        with col: st.markdown(card(ic,hd,tx),unsafe_allow_html=True)
    st.write("")
    l,r=st.columns(2,gap="large")
    with l:
        st.markdown("### Biomarker transformations")
        st.latex(r"\mathrm{Ratio}=\frac{A\beta42}{A\beta40}")
        st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
    with r:
        st.markdown("### Why Aβ42 and Aβ40?")
        st.write("The project tests whether simultaneous quantitative information from both amyloid peptides can be translated into a calibrated estimate of cerebral amyloid pathology, and whether retaining both dimensions adds value beyond the ratio alone.")
        st.markdown('<div class="info"><b>Contemporary context:</b> AMBER should not claim universal superiority over p-tau217. Where feasible, p-tau217 can be included as a contemporary comparator.</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="notice"><b>IP safeguard:</b> Unpublished DNA architecture details, recognition sequences, fabrication parameters, and other potentially patent-relevant implementation details are intentionally not exposed in V0.1.</div>',unsafe_allow_html=True)

elif page=="Model & Validation":
    st.markdown('<div class="kicker">Evidence layer</div><div class="title">Model & Validation</div>',unsafe_allow_html=True)
    st.markdown('<div class="notice"><b>V0.1 intentionally contains no real AMBER performance metrics.</b> ROC, calibration, Brier-score, decision-curve, threshold and external-validation outputs will appear only after real data are analysed.</div>',unsafe_allow_html=True)
    st.write("")
    p1,p2,p3=st.columns(3,gap="large")
    with p1: st.markdown('<div class="placeholder"><div><b>ROC / discrimination</b><br>Awaiting outcome-labelled clinical data</div></div>',unsafe_allow_html=True)
    with p2: st.markdown('<div class="placeholder"><div><b>Calibration</b><br>Awaiting model derivation and validation</div></div>',unsafe_allow_html=True)
    with p3: st.markdown('<div class="placeholder"><div><b>Decision-curve analysis</b><br>Awaiting clinically defined thresholds</div></div>',unsafe_allow_html=True)
    st.write("")
    df=pd.DataFrame([
        ["Aβ40 alone","Planned","Single-biomarker comparator"],
        ["Aβ42 alone","Planned","Single-biomarker comparator"],
        ["Aβ42/Aβ40 ratio","Planned","Conventional amyloid-ratio comparator"],
        ["AMBER-B","Planned","Primary biomarker-only model"],
        ["AMBER-C","Planned","Prespecified age/sex extension"],
        ["p-tau217","Optional","Contemporary comparator if available"],
        ["p-tau217/Aβ42","Optional","Contemporary ratio comparator if available"],
    ],columns=["Model / biomarker","Status","Purpose"])
    st.dataframe(df,hide_index=True,use_container_width=True)
    a,b,c=st.columns(3,gap="large")
    with a: st.markdown(card("🎯","Discrimination","AUROC with confidence intervals; sensitivity, specificity, PPV and NPV at locked thresholds."),unsafe_allow_html=True)
    with b: st.markdown(card("📏","Calibration","Calibration intercept/slope, calibration plot and Brier score."),unsafe_allow_html=True)
    with c: st.markdown(card("⚖️","Clinical utility","Decision-curve analysis plus prespecified rule-out and rule-in strategies."),unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="info"><b>Model-lock principle:</b> preprocessing, coefficients, calibration and thresholds are frozen before independent external validation. Later recalibration becomes a new model version.</div>',unsafe_allow_html=True)

elif page=="Longitudinal Monitoring":
    st.markdown('<div class="kicker">Future research module</div><div class="title">Longitudinal Monitoring</div>',unsafe_allow_html=True)
    st.markdown('<div class="info"><b>Reserved in V0.1.</b> This module becomes scientifically active only when repeated-measure data and appropriate longitudinal validation are available.</div>',unsafe_allow_html=True)
    st.write("")
    left,right=st.columns([1.6,1],gap="large")
    with left:
        fig=go.Figure()
        fig.update_xaxes(title="Visit / time",showgrid=True,gridcolor="#E8EDF6")
        fig.update_yaxes(title="AMBER probability",range=[0,100],showgrid=True,gridcolor="#E8EDF6")
        fig.add_annotation(x=.5,y=.52,xref="paper",yref="paper",text="<b>No longitudinal dataset loaded</b><br>Interface preview only",showarrow=False,font=dict(size=18,color="#667085"))
        fig.update_layout(height=380,paper_bgcolor="white",plot_bgcolor="#FBFCFF",margin=dict(l=35,r=20,t=20,b=35))
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown(card("📆","Trajectory view","Future repeated Aβ40, Aβ42, ratio, and AMBER probability trajectories."),unsafe_allow_html=True)
        st.write("")
        st.markdown(card("🧪","Assay metadata","Track assay version, batch, collection date, and longitudinal QC context."),unsafe_allow_html=True)
        st.write("")
        st.markdown(card("📤","Research export","Export repeated-measure records for validated longitudinal analysis."),unsafe_allow_html=True)

else:
    st.markdown('<div class="kicker">Scientific information</div><div class="title">About AMBER</div>',unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1 style="font-size:2.05rem;">A molecular-to-pathology research architecture</h1><p>AMBER is being developed to connect nanoscale molecular measurement with probabilistic assessment of cerebral amyloid pathology. V0.1 is a software prototype and does not contain a clinically derived AMBER equation.</p></div>',unsafe_allow_html=True)
    st.write("")
    a,b,c=st.columns(3,gap="large")
    with a: st.markdown(card("✅","Intended research use","Support assay-development studies, model derivation, validation, reproducible computation, and future longitudinal research."),unsafe_allow_html=True)
    with b: st.markdown(card("⛔","What AMBER is not","Not currently an Alzheimer's disease diagnosis, stand-alone diagnostic test, or substitute for PET, CSF testing, or clinical assessment."),unsafe_allow_html=True)
    with c: st.markdown(card("🔒","Current status","Application: V0.1 prototype. Model: demonstration only. Clinical coefficients, calibration and thresholds: not yet derived."),unsafe_allow_html=True)
    st.write("")
    st.markdown("### Scientific development path")
    cols=st.columns(6)
    for col,(n,h,t) in zip(cols,[("1","Analytical","DNA Compass validation"),("2","Clinical","PET-linked cohort"),("3","Derivation","AMBER-B / C"),("4","Internal","Bootstrap validation"),("5","Lock","Freeze model"),("6","External","Independent validation")]):
        with col: st.markdown(f'<div class="card"><div class="ct">{n}. {h}</div><div class="cb">{t}</div></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="notice"><b>IP / disclosure note:</b> potentially novel assay engineering details should remain outside the public application until institutional intellectual-property review and patent strategy are complete.</div>',unsafe_allow_html=True)

st.markdown(f'<div class="footer"><b>{APP_VERSION}</b> · Research prototype only · Demonstration outputs are not intended for diagnosis, patient management, or manuscript performance claims.</div>',unsafe_allow_html=True)
