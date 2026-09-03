import streamlit as st
import plotly.graph_objects as go
import math

MODEL = {
    "coefficients": {"intercept": -1.70, "R": -1.10, "M": 0.20, "age": 0.012, "sex": 0.15}
}
ASSAY = {"Aβ40_range": [20.0, 2000.0], "Aβ42_range": [2.0, 200.0]}

def demo_predict(model, ab40, ab42, age, sex):
    if ab40 <= 0 or ab42 <= 0:
        raise ValueError("Aβ40 and Aβ42 must both be greater than zero.")
    ratio = ab42 / ab40
    r = math.log10(ratio)
    m = math.log10(math.sqrt(ab40 * ab42))
    c = model["coefficients"]
    sex_code = 1 if str(sex).strip().lower() == "female" else 0
    index = c["intercept"] + c["R"]*r + c["M"]*m + c["age"]*age + c["sex"]*sex_code
    p = 1.0 / (1.0 + math.exp(-index))
    return {"ratio": ratio, "R": r, "M": m, "index": index, "probability": p, "score": 100*p}

st.set_page_config(page_title="AMBER V0.1", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1rem;padding-bottom:2rem}
.hero{background:linear-gradient(105deg,#071d49,#0c326f);color:white;border-radius:16px;padding:24px 28px;margin-bottom:14px}
.hero h1{margin:0;font-size:2.2rem}.hero p{margin:6px 0 0;opacity:.92}
.badge{display:inline-block;margin-top:10px;padding:5px 11px;border-radius:999px;background:#eef4ff;color:#0b2d6b;font-weight:700;font-size:.82rem}
h1,h2,h3{color:#08245b}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🧠 <span style="color:#f4b72d">AMBER</span> Score Platform</h1>
<p>Blood-based research platform for estimation of cerebral amyloid positivity.</p>
<span class="badge">V0.1 · RESEARCH PROTOTYPE · DEMONSTRATION ONLY</span>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", [
    "Home",
    "AMBER Calculator",
    "DNA Compass / Method",
    "Model & Validation",
    "Longitudinal Monitoring",
    "About / Scientific Information",
])
st.sidebar.divider()
st.sidebar.warning("Prototype only. Do not use for diagnosis or patient care.")

if page == "Home":
    st.title("From blood biomarkers to cerebral amyloid probability")
    st.write("AMBER is being developed to connect quantitative plasma Aβ40 and Aβ42 measurements with a transparent computational model that estimates the probability of cerebral amyloid positivity.")
    c1,c2,c3=st.columns(3)
    with c1:
        st.subheader("1. Measure")
        st.write("Quantify plasma Aβ40 and Aβ42 using the DNA Compass assay.")
    with c2:
        st.subheader("2. Transform")
        st.write("Derive the Aβ42/Aβ40 ratio and interpretable log-transformed features.")
    with c3:
        st.subheader("3. Estimate")
        st.write("Convert molecular measurements into an individualized probability using a future locked model.")
    st.info("V0.1 uses illustrative coefficients only so that the software workflow and UI can be tested.")

elif page == "AMBER Calculator":
    st.title("AMBER Calculator — Prototype")
    left, center, right = st.columns([0.95,1.25,1.0], gap="large")
    with left:
        st.subheader("1. Input values")
        ab40=st.number_input("Plasma Aβ40 (pg/mL)",min_value=0.01,value=285.0,step=1.0,format="%.2f")
        st.caption(f"Demo interface range: {ASSAY['Aβ40_range'][0]:g}–{ASSAY['Aβ40_range'][1]:g} pg/mL")
        ab42=st.number_input("Plasma Aβ42 (pg/mL)",min_value=0.01,value=18.5,step=0.1,format="%.2f")
        st.caption(f"Demo interface range: {ASSAY['Aβ42_range'][0]:g}–{ASSAY['Aβ42_range'][1]:g} pg/mL")
        age=st.number_input("Age (years)",min_value=18,max_value=100,value=68,step=1)
        sex=st.radio("Sex",["Male","Female"],horizontal=True,index=1)
        run=st.button("Calculate DEMO score",type="primary",use_container_width=True)
        st.caption("The ratio, R and M are calculated internally. Current coefficients are placeholders.")
    with center:
        st.subheader("2. Result")
        if run:
            if not (ASSAY['Aβ40_range'][0] <= ab40 <= ASSAY['Aβ40_range'][1]): st.warning("Aβ40 is outside the configured demo interface range.")
            if not (ASSAY['Aβ42_range'][0] <= ab42 <= ASSAY['Aβ42_range'][1]): st.warning("Aβ42 is outside the configured demo interface range.")
            out=demo_predict(MODEL,ab40,ab42,age,sex)
            fig=go.Figure(go.Indicator(mode="gauge+number",value=out['score'],number={'suffix':'/100','font':{'size':52}},title={'text':'Illustrative AMBER probability'},gauge={'axis':{'range':[0,100]},'bar':{'color':'#08245b'},'steps':[{'range':[0,33],'color':'#dff3df'},{'range':[33,67],'color':'#fff1bd'},{'range':[67,100],'color':'#ffdada'}]}))
            fig.update_layout(height=350,margin=dict(l=20,r=20,t=45,b=10))
            st.plotly_chart(fig,use_container_width=True)
            st.error("DEMONSTRATION OUTPUT ONLY — not a validated clinical AMBER result.")
            a,b,c=st.columns(3)
            a.metric("Aβ42/Aβ40",f"{out['ratio']:.4f}")
            b.metric("R",f"{out['R']:.3f}")
            c.metric("M",f"{out['M']:.3f}")
        else:
            st.info("Enter values and click Calculate DEMO score.")
    with right:
        st.subheader("3. Scientific transparency")
        st.markdown("**Derived features**")
        st.latex(r"R=\log_{10}(A\beta42/A\beta40)")
        st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
        st.markdown("**Prototype AMBER-C form**")
        st.latex(r"I=\beta_0+\beta_RR+\beta_MM+\beta_A Age+\beta_S Sex")
        st.latex(r"P=\frac{1}{1+e^{-I}}")
        st.warning("Final coefficients must be estimated from real PET-linked clinical data.")

elif page == "DNA Compass / Method":
    st.title("DNA Compass / Method")
    st.write("This page describes the intended molecular-to-computational workflow. Experimental assay details will be added once analytically locked.")
    cols=st.columns(6)
    steps=[("1","Sample","Plasma"),("2","DNA Compass","Dual recognition"),("3","Aβ42 / Aβ40","Simultaneous measurement"),("4","Optical readout","Quantification"),("5","Transform","Ratio, R, M"),("6","AMBER","Probability")]
    for col,(n,t,d) in zip(cols,steps):
        with col:
            st.markdown(f"### {n}"); st.markdown(f"**{t}**"); st.caption(d)
    st.divider()
    st.subheader("Why Aβ42 and Aβ40?")
    st.write("The project tests whether simultaneous quantitative measurement of both amyloid peptides can be translated into a calibrated estimate of cerebral amyloid pathology.")
    st.info("AMBER should not claim that Aβ42/Aβ40 is universally superior to p-tau217. p-tau217 can be included as a contemporary comparator where available.")

elif page == "Model & Validation":
    st.title("Model & Validation")
    st.warning("V0.1 intentionally contains no real AMBER performance metrics. Real ROC, calibration and decision-curve outputs will appear only after real data are analyzed.")
    st.subheader("Planned comparisons")
    st.markdown("1. Aβ40 alone  \n2. Aβ42 alone  \n3. Aβ42/Aβ40 ratio  \n4. AMBER-B  \n5. AMBER-C  \n6. Optional p-tau217  \n7. Optional p-tau217/Aβ42")
    a,b,c=st.columns(3)
    with a: st.markdown("**Discrimination**"); st.write("AUROC, sensitivity, specificity, PPV, NPV")
    with b: st.markdown("**Calibration**"); st.write("Calibration intercept/slope, plots, Brier score")
    with c: st.markdown("**Clinical utility**"); st.write("Decision-curve analysis and locked thresholds")

elif page == "Longitudinal Monitoring":
    st.title("Longitudinal Monitoring")
    st.info("Reserved in V0.1. This module will only be activated when repeated-measure data and longitudinal validation are available.")
    st.markdown("- repeated Aβ40/Aβ42 measurements\n- ratio trajectory\n- AMBER probability trajectory\n- assay-batch tracking\n- research export")

else:
    st.title("About / Scientific Information")
    st.subheader("What AMBER is")
    st.write("A research platform intended to connect nanoscale molecular measurement with probabilistic assessment of cerebral amyloid pathology.")
    st.subheader("What AMBER is not")
    st.markdown("- Not currently a diagnostic test.\n- Not a substitute for PET, CSF testing or clinical assessment.\n- Not validated for patient management.\n- Not an Alzheimer's disease diagnosis.")
    st.subheader("Current status")
    st.write("**Application:** V0.1 research prototype")
    st.write("**Model:** demonstration only")
    st.write("**Clinical coefficients:** not yet derived")

st.divider()
st.caption("AMBER V0.1 — Research prototype only. Demonstration outputs are not intended for diagnosis, patient management or manuscript performance claims.")
