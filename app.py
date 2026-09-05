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
    with open("assets/hitsz_logo_white.png", "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode("ascii")
except Exception:
    LOGO_B64 = ""

try:
    with open("assets/amber_header_science.png", "rb") as f:
        HEADER_SCIENCE_B64 = base64.b64encode(f.read()).decode("ascii")
except Exception:
    HEADER_SCIENCE_B64 = ""

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

/* ==========================================================
   LOCKED HOME PAGE VISUAL MATCH PASS — 1536 × 1024 reference
   ========================================================== */
html, body, .stApp { margin:0 !important; padding:0 !important; }
header[data-testid="stHeader"], div[data-testid="stToolbar"] { display:none !important; height:0 !important; }
.block-container{width:100% !important;max-width:1536px !important;margin:0 auto !important;padding-left:68px !important;padding-right:68px !important;padding-top:0 !important;padding-bottom:12px !important;box-sizing:border-box !important;}
.hero{height:166px !important;min-height:166px !important;box-sizing:border-box !important;margin:0 -45px 14px -45px !important;padding:0 !important;border-radius:18px !important;background:linear-gradient(104deg,#05285E 0%,#062D69 46%,#0A4A92 100%) !important;box-shadow:0 12px 26px rgba(3,38,85,.10) !important;position:relative !important;overflow:hidden !important;}
.hero:before,.hero:after{display:none !important;content:none !important;}
.hero-left{position:absolute;z-index:4;left:45px;top:0;height:166px;display:grid;grid-template-columns:118px 1px 650px;column-gap:28px;align-items:center;}
.hero-logo-wrap{display:flex;align-items:center;justify-content:center;height:100%;}.hero-logo{width:102px !important;height:102px !important;object-fit:contain !important;filter:none !important;}.hero-separator{width:1px;height:100px;background:rgba(255,255,255,.64);}.hero-copy{align-self:center;margin-left:8px;}.hero-title{font-size:41px !important;line-height:1.02 !important;font-weight:850 !important;letter-spacing:-1.4px !important;margin:0 !important;white-space:nowrap;}.hero-title .amber{color:#F5B72A !important;}.hero-sub{font-size:16px !important;line-height:1.35 !important;margin-top:8px !important;color:#F0F5FC !important;}.badges{display:flex !important;gap:10px !important;flex-wrap:nowrap !important;margin-top:16px !important;}.badge{height:31px;box-sizing:border-box;display:flex;align-items:center;padding:0 13px !important;border-radius:999px !important;background:rgba(255,255,255,.07) !important;border:1px solid rgba(255,255,255,.28) !important;color:#fff !important;font-size:10.5px !important;font-weight:800 !important;white-space:nowrap;}.hero-science-art{position:absolute;z-index:2;right:132px;top:0;width:438px;height:166px;object-fit:cover;object-position:center;pointer-events:none;}.hero-slogan{position:absolute;z-index:4;right:43px;top:42px;width:104px;color:#fff;text-align:left;font-size:11px;line-height:1.75;letter-spacing:3.2px;font-weight:650;text-transform:uppercase;}.hero-slogan-line{width:43px;height:2px;background:#F4B42D;margin-top:10px;}
div[data-testid="stSegmentedControl"]{width:max-content !important;max-width:100%;margin:0 0 21px 0 !important;padding:0 !important;}div[data-testid="stSegmentedControl"] > div{gap:0 !important;width:max-content !important;}div[data-testid="stSegmentedControl"] button{flex:0 0 auto !important;width:auto !important;min-height:38px !important;height:38px !important;border-radius:0 !important;padding:0 20px !important;font-size:13px !important;font-weight:500 !important;border-color:#D3DDE8 !important;background:#fff !important;color:#172A45 !important;}div[data-testid="stSegmentedControl"] button:first-child{border-radius:7px 0 0 7px !important;}div[data-testid="stSegmentedControl"] button:last-child{border-radius:0 7px 7px 0 !important;}div[data-testid="stSegmentedControl"] button[aria-checked="true"]{background:#FFF4F2 !important;border:1px solid #FF6F66 !important;color:#FF4D45 !important;box-shadow:none !important;}
.home-title-row{display:grid;grid-template-columns:minmax(0,1fr) 510px;align-items:center;column-gap:30px;margin:0 0 17px 0;min-height:104px;}.home-title-left{align-self:start;padding-top:1px;}.home-kicker{color:#0B4EA1;font-size:12px;line-height:1;font-weight:850;text-transform:uppercase;letter-spacing:1.5px;margin:0 0 12px 0;}.home-title{color:#06285F;font-size:37px;line-height:1.06;font-weight:850;letter-spacing:-.8px;margin:0 0 7px 0;}.home-sub{color:#617892;font-size:16px;line-height:1.3;margin:0;}.home-brand-message{text-align:right;align-self:center;padding-top:7px;}.home-brand-main{color:#0B4EA1;font-size:13px;letter-spacing:5px;font-weight:500;white-space:nowrap;}.home-brand-sub{color:#5D79A3;font-size:10.5px;letter-spacing:1.4px;margin-top:25px;white-space:nowrap;}.home-brand-ai{position:relative;display:inline-block;padding:0 6px;}.home-brand-ai:after{content:"";position:absolute;left:3px;right:3px;bottom:-13px;height:2px;background:#F4B42D;}
.home-question{height:118px;box-sizing:border-box;display:grid;grid-template-columns:108px 1px 1fr;align-items:center;border:1px solid #B8D8F6;border-radius:14px;background:linear-gradient(90deg,#F5FAFF 0%,#EDF6FF 100%);padding:0 28px 0 28px;margin:0 0 24px 0;}.home-qicon{width:70px;height:70px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#275FA5,#0A438D);color:#fff;font-size:34px;font-weight:800;border:5px solid #D9EAFE;box-shadow:0 0 0 1px #8BB7E7;}.home-qsep{width:1px;height:72px;background:#93B9E1;}.home-qcopy{padding-left:28px;}.home-qlabel{color:#0B4EA1;font-size:12px;font-weight:850;letter-spacing:1.4px;margin-bottom:10px;}.home-qtext{color:#0A2C60;font-size:17px;line-height:1.45;max-width:1150px;}
.home-section-title{color:#06285F;font-size:22px;line-height:1;font-weight:850;margin:0 0 14px 0;}.home-section-title.path{margin-top:24px;}
.home-matters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:25px;margin:0;}.home-matter-card{height:136px;box-sizing:border-box;border:1px solid #C8DFF5;border-radius:13px;background:#fff;display:flex;align-items:center;padding:18px 22px;gap:22px;}.home-matter-card.amber{background:linear-gradient(90deg,#FFFDF7,#FFF8E8);border-color:#F0D495;}.home-icon-disc{width:68px;height:68px;min-width:68px;border-radius:50%;background:#E8F3FF;display:flex;align-items:center;justify-content:center;color:#1768B2;}.home-matter-card.amber .home-icon-disc{background:#FFF0C8;color:#E0A113;}.home-icon-disc svg{width:43px;height:43px;display:block;}.home-matter-title{color:#06285F;font-size:16px;font-weight:850;line-height:1.25;margin-bottom:7px;}.home-matter-body{color:#526D8E;font-size:14px;line-height:1.42;}
.home-pathway{display:grid;grid-template-columns:1fr 26px 1fr 26px 1fr 26px 1fr 26px 1fr;gap:0;align-items:center;}.home-path-card{height:166px;box-sizing:border-box;border:1px solid #C8DFF5;border-radius:13px;background:#fff;position:relative;text-align:center;padding:20px 16px 12px;}.home-step-num{position:absolute;left:15px;top:14px;width:34px;height:34px;border-radius:50%;background:#E6F2FF;color:#0B4EA1;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:850;}.home-path-icon{height:48px;display:flex;align-items:center;justify-content:center;margin:0 auto 5px;color:#1768B2;}.home-path-icon svg{width:42px;height:42px;display:block;}.home-path-icon.red{color:#D95E55;}.home-path-title{color:#06285F;font-size:15px;font-weight:850;margin-bottom:6px;line-height:1;}.home-path-body{color:#526D8E;font-size:13.5px;line-height:1.35;max-width:190px;margin:0 auto;}.home-path-arrow{display:flex;align-items:center;justify-content:center;color:#8DA7C4;}.home-path-arrow svg{width:22px;height:22px;}
.home-stage{height:48px;box-sizing:border-box;border:1px solid #E8BD55;border-radius:12px;background:#FFF8E6;display:flex;align-items:center;gap:14px;padding:0 18px;margin-top:17px;color:#6D5414;font-size:13px;line-height:1;white-space:nowrap;overflow:hidden;}.home-stage-icon{width:28px;height:28px;display:flex;align-items:center;justify-content:center;color:#D89400;flex:0 0 auto;}.home-stage-icon svg{width:26px;height:26px;}.home-stage strong{font-weight:850;}
.footer.home-footer{height:49px;box-sizing:border-box;border-top:1px solid #CFE0F2;margin-top:16px !important;padding-top:13px !important;font-size:10.5px !important;color:#68809A;display:grid !important;grid-template-columns:1fr 1fr 1fr;align-items:start;}.footer.home-footer>div:nth-child(1){text-align:left}.footer.home-footer>div:nth-child(2){text-align:center}.footer.home-footer>div:nth-child(3){text-align:right}
@media(max-width:1100px){.block-container{padding-left:32px !important;padding-right:32px !important;}.hero{margin-left:-18px !important;margin-right:-18px !important;}.hero-left{left:24px;grid-template-columns:90px 1px 1fr;column-gap:18px}.hero-logo{width:78px !important;height:78px !important}.hero-title{font-size:31px !important}.hero-science-art{opacity:.65;right:90px}.hero-slogan{right:18px}.home-title-row{grid-template-columns:1fr}.home-brand-message{display:none}.home-matters{gap:12px}.home-pathway{grid-template-columns:1fr 18px 1fr 18px 1fr;row-gap:12px}.home-stage{white-space:normal;height:auto;min-height:48px;padding-top:9px;padding-bottom:9px}.home-path-card{height:166px}}
@media(max-width:760px){.block-container{padding-left:16px !important;padding-right:16px !important}.hero{margin-left:-8px !important;margin-right:-8px !important;height:150px !important;min-height:150px !important}.hero-left{left:16px;height:150px;grid-template-columns:65px 1px 1fr;column-gap:12px}.hero-logo{width:58px !important;height:58px !important}.hero-separator{height:72px}.hero-title{font-size:25px !important}.hero-sub{font-size:12px !important}.badges{gap:4px !important;margin-top:10px !important}.badge{font-size:7.5px !important;padding:0 7px !important;height:24px}.hero-science-art,.hero-slogan{display:none}.home-title-row{min-height:auto}.home-title{font-size:29px}.home-sub{font-size:14px}.home-question{height:auto;min-height:118px;grid-template-columns:76px 1px 1fr;padding:12px 14px}.home-qicon{width:58px;height:58px;font-size:29px}.home-qcopy{padding-left:16px}.home-qtext{font-size:14px}.home-matters{grid-template-columns:1fr}.home-matter-card{height:auto;min-height:120px}.home-pathway{display:block}.home-path-card{height:auto;min-height:150px;margin-bottom:9px}.home-path-arrow{transform:rotate(90deg);height:20px}.footer.home-footer{height:auto;grid-template-columns:1fr;gap:4px}.footer.home-footer>div{text-align:left !important}}


/* ==========================================================
   LOCKED CALCULATOR PAGE VISUAL MATCH PASS — 1536 × 1024
   Scoped to Calculator-specific keyed containers/components.
   ========================================================== */
.calc-page-title-row{display:grid;grid-template-columns:minmax(0,1fr) 510px;align-items:center;column-gap:30px;min-height:75px;margin:0 0 12px 0;}
.calc-page-title-left{align-self:center;}
.calc-page-kicker{color:#0B4EA1;font-size:12px;line-height:1;font-weight:850;text-transform:uppercase;letter-spacing:1.5px;margin:0 0 12px 0;}
.calc-page-title{color:#06285F;font-size:35px;line-height:1.04;font-weight:850;letter-spacing:-.7px;margin:0;}
.calc-brand-message{text-align:right;align-self:center;padding-top:3px;}
.calc-brand-main{color:#0B4EA1;font-size:13px;letter-spacing:5px;font-weight:500;white-space:nowrap;}
.calc-brand-sub{color:#5D79A3;font-size:10.5px;letter-spacing:1.4px;margin-top:25px;white-space:nowrap;}
.calc-brand-ai{position:relative;display:inline-block;padding:0 6px;}.calc-brand-ai:after{content:"";position:absolute;left:3px;right:3px;bottom:-13px;height:2px;background:#F4B42D;}

.st-key-amber_input_panel,
.st-key-amber_results_panel,
.st-key-amber_scientific_panel{
  min-height:574px !important;
  height:574px !important;
  box-sizing:border-box !important;
  border:1px solid #BFD8F0 !important;
  border-radius:13px !important;
  background:linear-gradient(180deg,#FFFFFF 0%,#FCFEFF 100%) !important;
  padding:15px 18px !important;
  overflow:visible !important;
  box-shadow:none !important;
}
.st-key-amber_input_panel [data-testid="stVerticalBlock"],
.st-key-amber_results_panel [data-testid="stVerticalBlock"],
.st-key-amber_scientific_panel [data-testid="stVerticalBlock"]{gap:.42rem !important;}

.calc-panel-head{display:grid;grid-template-columns:50px 1fr;align-items:start;column-gap:13px;margin:0 0 10px 0;}
.calc-panel-num{width:48px;height:48px;border-radius:50%;background:linear-gradient(180deg,#DDEEFF,#CFE6FF);color:#073F86;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:850;}
.calc-panel-title{color:#06285F;font-size:22px;font-weight:850;line-height:1.08;margin:3px 0 4px;}
.calc-panel-sub{color:#607B9A;font-size:12.5px;line-height:1.36;}
.calc-section-label{color:#06285F;font-size:15px;font-weight:850;margin:8px 0 1px;}
.calc-biomarker-title{color:#06285F;font-size:19px;font-weight:850;margin:7px 0 5px;}

.st-key-amber_input_panel label p{color:#173150 !important;font-size:12.5px !important;}
.st-key-amber_input_panel div[data-baseweb="select"] > div,
.st-key-amber_input_panel div[data-testid="stNumberInputContainer"]{min-height:42px !important;background:#F0F3F7 !important;border:0 !important;border-radius:8px !important;box-shadow:none !important;}
.st-key-amber_input_panel div[data-testid="stNumberInputContainer"] input{background:#F0F3F7 !important;color:#152B49 !important;font-size:13px !important;}
.st-key-amber_input_panel div[data-testid="stNumberInputContainer"] button{background:#F0F3F7 !important;border-left:1px solid #E1E7EE !important;color:#082A5B !important;}
.st-key-amber_input_panel [data-testid="stCheckbox"]{margin-top:2px !important;}
.st-key-amber_input_panel [data-testid="stCheckbox"] label{align-items:center !important;}

.st-key-amber_input_panel div[data-testid="stFormSubmitButton"] button{width:100% !important;height:47px !important;min-height:47px !important;margin-top:5px !important;border-radius:8px !important;background:linear-gradient(90deg,#073477,#0A4B98) !important;color:#fff !important;font-size:13px !important;font-weight:800 !important;letter-spacing:.1px !important;display:flex !important;align-items:center !important;justify-content:center !important;gap:11px !important;}
.st-key-amber_input_panel div[data-testid="stFormSubmitButton"] button:before{content:"";width:18px;height:18px;display:inline-block;background-size:18px 18px;background-repeat:no-repeat;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='5' y='2' width='14' height='20' rx='2'/%3E%3Cpath d='M8 6h8v4H8zM8 14h2M12 14h2M16 14h0M8 18h2M12 18h2M16 18h0'/%3E%3C/svg%3E");}
.calc-info-callout{margin-top:9px;border:1px solid #9DCBF5;border-radius:9px;background:linear-gradient(90deg,#F4FAFF,#ECF6FF);min-height:61px;box-sizing:border-box;display:grid;grid-template-columns:34px 1fr;align-items:center;column-gap:9px;padding:8px 11px;color:#0B4EA1;font-size:12.5px;line-height:1.4;}
.calc-info-icon{width:25px;height:25px;border-radius:50%;background:#0B59B0;color:#fff;display:flex;align-items:center;justify-content:center;}.calc-info-icon svg{width:15px;height:15px;}

.locked-gauge{position:relative;height:208px;margin:2px 0 0;}
.locked-gauge svg{width:100%;height:185px;display:block;overflow:visible;}
.locked-gauge .g50{position:absolute;left:50%;top:2px;transform:translateX(-50%);font-size:13px;color:#244467;}
.locked-gauge .g0{position:absolute;left:28px;bottom:40px;font-size:13px;color:#26496F;}
.locked-gauge .g100{position:absolute;right:27px;bottom:40px;font-size:13px;color:#26496F;}
.locked-gauge-score{position:absolute;left:50%;top:78px;transform:translateX(-50%);text-align:center;color:#052C68;line-height:1;}
.locked-gauge-score .main{font-size:48px;font-weight:850;letter-spacing:-1.2px;}
.locked-gauge-score .den{font-size:24px;font-weight:400;color:#7187A3;margin-top:8px;}
.locked-gauge-caption{position:absolute;left:0;right:0;bottom:3px;text-align:center;color:#607995;font-size:13px;}
.calc-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:1px;}
.calc-metric{height:76px;box-sizing:border-box;border:1px solid #B8D6F2;border-radius:9px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.calc-metric-label{color:#6F8AA7;font-size:10.5px;font-weight:750;margin-bottom:5px;}.calc-metric-value{color:#052D69;font-size:22px;font-weight:850;line-height:1;}
.calc-demo-alert{margin-top:9px;border:1px solid #FF9A92;border-radius:9px;background:#FFF0EF;min-height:73px;box-sizing:border-box;display:grid;grid-template-columns:38px 1fr;align-items:center;column-gap:9px;padding:9px 12px;color:#D9362D;}
.calc-warning-icon{width:31px;height:31px;color:#E4443A;}.calc-warning-icon svg{width:31px;height:31px;display:block;}.calc-demo-title{font-size:12.5px;font-weight:850;line-height:1.2;margin-bottom:3px;}.calc-demo-copy{font-size:12px;line-height:1.35;}

.st-key-amber_results_panel .stDownloadButton button{height:46px !important;min-height:46px !important;border-radius:8px !important;border:1px solid #2C72D0 !important;background:#fff !important;color:#07377A !important;font-size:13px !important;font-weight:800 !important;display:flex !important;align-items:center !important;justify-content:center !important;gap:10px !important;}
.st-key-amber_results_panel .stDownloadButton button:before{content:"";width:19px;height:19px;display:inline-block;background-size:19px 19px;background-repeat:no-repeat;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230B59B0' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3v12M7 10l5 5 5-5M4 19h16'/%3E%3C/svg%3E");}

.calc-science-intro{color:#526F91;font-size:12.5px;line-height:1.42;margin:0 0 8px 0;}
.calc-divider{height:1px;background:#C9D9EA;margin:7px 0 8px;}
.calc-science-heading{color:#06285F;font-size:14px;font-weight:850;margin:0 0 1px;}
.st-key-amber_scientific_panel [data-testid="stLatex"]{margin:0 !important;padding:0 !important;}
.st-key-amber_scientific_panel .katex-display{margin:.26em 0 .34em !important;}
.st-key-amber_scientific_panel .katex{color:#0B2B5C !important;font-size:1.12em !important;}
.calc-safeguard{margin-top:6px;border:1px solid #E9C268;border-radius:9px;background:#FFF8E6;min-height:72px;box-sizing:border-box;display:grid;grid-template-columns:34px 1fr;align-items:center;column-gap:10px;padding:9px 11px;color:#6B5519;font-size:12px;line-height:1.35;}
.calc-bulb{width:29px;height:29px;color:#E0A315;}.calc-bulb svg{width:29px;height:29px;display:block;}

.calc-workflow{height:92px;box-sizing:border-box;border:1px solid #BFD9F1;border-radius:12px;background:#fff;display:grid;grid-template-columns:360px 1px 1fr;align-items:center;margin:11px 0 8px 0;overflow:hidden;}
.calc-workflow-intro{padding:0 20px;}.calc-workflow-title{color:#06285F;font-size:18px;font-weight:850;line-height:1.1;margin-bottom:6px;}.calc-workflow-sub{color:#66809E;font-size:12.5px;}.calc-workflow-sep{width:1px;height:58px;background:#C7DAED;}
.calc-workflow-steps{display:grid;grid-template-columns:1fr 30px 1fr 30px 1fr 30px 1fr;align-items:center;padding:0 18px;column-gap:2px;}
.calc-work-step{display:grid;grid-template-columns:34px 42px 1fr;align-items:center;column-gap:9px;min-width:0;}.calc-work-num{width:34px;height:34px;border-radius:50%;background:#E6F2FF;color:#0B4EA1;display:flex;align-items:center;justify-content:center;font-weight:850;font-size:14px;}.calc-work-icon{width:40px;height:40px;color:#0B59B0;display:flex;align-items:center;justify-content:center;}.calc-work-icon svg{width:36px;height:36px;}.calc-work-title{color:#06285F;font-size:12.5px;font-weight:850;line-height:1.1;margin-bottom:3px;}.calc-work-copy{color:#5E7897;font-size:10.7px;line-height:1.28;}.calc-work-arrow{color:#8FA8C3;display:flex;align-items:center;justify-content:center;}.calc-work-arrow svg{width:20px;height:20px;}

@media(max-width:1199px){
  .calc-page-title-row{grid-template-columns:1fr;}.calc-brand-message{display:none;}
  .st-key-amber_input_panel,.st-key-amber_results_panel,.st-key-amber_scientific_panel{height:auto !important;min-height:0 !important;}
  .calc-workflow{height:auto;grid-template-columns:1fr;margin-bottom:10px;}.calc-workflow-sep{display:none}.calc-workflow-steps{grid-template-columns:1fr;row-gap:12px;padding:14px 18px}.calc-work-arrow{transform:rotate(90deg)}.calc-workflow-intro{padding:15px 18px 5px}
}

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


def _arc_path(cx, cy, r, start_deg, end_deg):
    """SVG arc path helper."""
    import math as _m
    def pt(d):
        rad = _m.radians(d)
        return cx + r * _m.cos(rad), cy - r * _m.sin(rad)
    x1,y1 = pt(start_deg)
    x2,y2 = pt(end_deg)
    large = 1 if abs(end_deg-start_deg) > 180 else 0
    sweep = 0 if end_deg > start_deg else 1
    return f"M {x1:.2f} {y1:.2f} A {r} {r} 0 {large} {sweep} {x2:.2f} {y2:.2f}"


def segmented_gauge_html(score):
    score = max(0.0, min(100.0, float(score)))
    cx, cy, r = 180, 174, 128
    palette = ['#9FCBF5','#82B8EC','#AFC1CB','#D5D7C5','#F5D47B','#F4B42D','#F0BF48','#E7EAF0','#E7EAF0','#E7EAF0']
    paths = []
    for i in range(10):
        lo, hi = i*10, (i+1)*10
        start = 180 - lo*1.8 + 0.7
        end = 180 - hi*1.8 - 0.7
        color = palette[i] if lo < score else '#E7EAF0'
        paths.append(f"<path d='{_arc_path(cx,cy,r,start,end)}' fill='none' stroke='{color}' stroke-width='24' stroke-linecap='butt'/>")
    return f"""
    <div class='locked-gauge'>
      <div class='g50'>50</div><div class='g0'>0</div><div class='g100'>100</div>
      <svg viewBox='0 0 360 205' aria-label='Illustrative AMBER software output gauge'>
        <path d='{_arc_path(cx,cy,r,180,0)}' fill='none' stroke='#E7EAF0' stroke-width='24'/>
        {''.join(paths)}
      </svg>
      <div class='locked-gauge-score'><div class='main'>{score:.1f}</div><div class='den'>/ 100</div></div>
      <div class='locked-gauge-caption'>Illustrative AMBER software output</div>
    </div>
    """


def build_amber_pdf(report):
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w,h = A4
    navy = HexColor('#06285F'); blue = HexColor('#0B4EA1'); grey = HexColor('#536B86'); amber = HexColor('#F4B42D')
    c.setFillColor(navy); c.rect(0,h-92,w,92,fill=1,stroke=0)
    c.setFillColor(amber); c.setFont('Helvetica-Bold',21); c.drawString(42,h-46,'AMBER')
    c.setFillColor(HexColor('#FFFFFF')); c.drawString(138,h-46,'Score Platform')
    c.setFont('Helvetica',9.5); c.drawString(42,h-65,'Research prototype summary - demonstration / derived features only')
    y = h-125
    c.setFillColor(navy); c.setFont('Helvetica-Bold',14); c.drawString(42,y,'AMBER Calculation Summary')
    y -= 28
    rows = [
      ('Application', report.get('application','AMBER V0.1')),
      ('Generated', report.get('generated_at','')),
      ('Configuration', report.get('configuration','')),
      ('A beta 40 (pg/mL)', str(report.get('inputs',{}).get('ab40_pg_ml',''))),
      ('A beta 42 (pg/mL)', str(report.get('inputs',{}).get('ab42_pg_ml',''))),
      ('A beta 42/A beta 40', f"{report.get('derived',{}).get('ratio',0):.4f}"),
      ('R', f"{report.get('derived',{}).get('R',0):.3f}"),
      ('M', f"{report.get('derived',{}).get('M',0):.3f}"),
    ]
    if report.get('inputs',{}).get('age') is not None:
        rows += [('Age', str(report['inputs']['age'])), ('Sex', str(report['inputs']['sex']))]
    if report.get('illustrative_score') is not None:
        rows += [('Illustrative output', f"{report['illustrative_score']:.1f}/100")]
    for label,val in rows:
        c.setFillColor(blue); c.setFont('Helvetica-Bold',9.5); c.drawString(42,y,label)
        c.setFillColor(grey); c.setFont('Helvetica',9.5); c.drawString(200,y,str(val)); y -= 20
    y -= 8
    c.setFillColor(HexColor('#A4312B')); c.setFont('Helvetica-Bold',9.5); c.drawString(42,y,'RESEARCH / DEMONSTRATION USE ONLY'); y -= 16
    c.setFillColor(grey); c.setFont('Helvetica',8.8)
    for line in [
      'This output is not a clinically validated AMBER score and is not intended for diagnosis or patient care.',
      'Final coefficients, calibration, operating thresholds and performance metrics require PET-linked clinical data',
      'and independent validation before any production clinical interpretation.'
    ]:
        c.drawString(42,y,line); y -= 13
    c.setStrokeColor(HexColor('#C9D9EA')); c.line(42,48,w-42,48)
    c.setFillColor(grey); c.setFont('Helvetica',7.5); c.drawString(42,34,'AMBER V0.1'); c.drawCentredString(w/2,34,'Model status: DEMONSTRATION ONLY'); c.drawRightString(w-42,34,'Research use only - Not a diagnostic test')
    c.save(); return buf.getvalue()

SVG_CALC_INFO = """<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.2' stroke-linecap='round'><circle cx='12' cy='12' r='9'/><path d='M12 10v7M12 7h.01'/></svg>"""
SVG_WARNING_TRI = """<svg viewBox='0 0 32 32' fill='currentColor'><path d='M16 3 30 28H2L16 3Z'/><rect x='14.7' y='10' width='2.6' height='9' rx='1.3' fill='white'/><circle cx='16' cy='23.2' r='1.7' fill='white'/></svg>"""
SVG_BULB = """<svg viewBox='0 0 32 32' fill='none' stroke='currentColor' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'><path d='M10 13a6 6 0 1 1 12 0c0 4-3 5-4 8h-4c-1-3-4-4-4-8Z'/><path d='M13 25h6M14 28h4'/></svg>"""
SVG_CLIPBOARD = """<svg viewBox='0 0 48 48' fill='none' stroke='currentColor' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'><rect x='10' y='8' width='28' height='34' rx='3'/><path d='M18 8V5h12v3M16 18h16M16 25h16M16 32h11'/></svg>"""
SVG_GEAR = """<svg viewBox='0 0 48 48' fill='none' stroke='currentColor' stroke-width='2.7' stroke-linecap='round' stroke-linejoin='round'><circle cx='24' cy='24' r='7'/><path d='m24 5 3 5 6 1 4-4 5 5-4 4 1 6 5 3-3 7-6-1-5 4v6h-8v-6l-5-4-6 1-3-7 5-3 1-6-4-4 5-5 4 4 6-1 3-5Z'/></svg>"""
SVG_REPORT = """<svg viewBox='0 0 48 48' fill='none' stroke='currentColor' stroke-width='2.7' stroke-linecap='round' stroke-linejoin='round'><path d='M12 5h18l7 7v31H12Z'/><path d='M30 5v9h7M18 21h13M18 27h13M18 33h9'/></svg>"""

logo_html = f'<img class="hero-logo" src="data:image/png;base64,{LOGO_B64}" alt="HIT Shenzhen">' if LOGO_B64 else '<div style="color:white;font-weight:800">HIT</div>'
header_science_html = f'<img class="hero-science-art" src="data:image/png;base64,{HEADER_SCIENCE_B64}" alt="Molecular brain and DNA artwork">' if HEADER_SCIENCE_B64 else ''

st.markdown(f'''
<div class="hero">
  <div class="hero-left">
    <div class="hero-logo-wrap">{logo_html}</div>
    <div class="hero-separator"></div>
    <div class="hero-copy">
      <div class="hero-title"><span class="amber">AMBER</span> Score Platform</div>
      <div class="hero-sub">Blood-based molecular research platform for estimation of cerebral amyloid positivity.</div>
      <div class="badges">
        <span class="badge">V0.1 · RESEARCH PROTOTYPE</span>
        <span class="badge">DNA COMPASS + COMPUTATIONAL INFERENCE</span>
        <span class="badge">NO CLINICAL VALIDATION CLAIMS</span>
      </div>
    </div>
  </div>
  {header_science_html}
  <div class="hero-slogan">MOLECULAR<br>INSIGHTS<br>FOR A CLEARER<br>TOMORROW<div class="hero-slogan-line"></div></div>
</div>
''', unsafe_allow_html=True)

SVG_BRAIN = """<svg viewBox='0 0 64 64' fill='none' stroke='currentColor' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'><path d='M31 13c-6-6-15-1-14 6-6 1-8 9-3 13-5 5-1 13 5 13 1 7 10 9 13 3V16c0-2-1-3-1-3Z'/><path d='M33 13c6-6 15-1 14 6 6 1 8 9 3 13 5 5 1 13-5 13-1 7-10 9-13 3V16c0-2 1-3 1-3Z'/><path d='M23 22c4 0 6 3 6 6M20 35c5-1 8 2 9 6M41 22c-4 0-6 3-6 6M44 35c-5-1-8 2-9 6'/></svg>"""
SVG_TUBES = """<svg viewBox='0 0 64 64' fill='none' stroke='currentColor' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><path d='M14 10h16M18 10v34a8 8 0 0 0 8 8h0a8 8 0 0 0 8-8V10'/><path d='M36 10h14M39 10v34a7 7 0 0 0 7 7h0a7 7 0 0 0 7-7V10'/><path d='M18 31h16M39 28h14' stroke-width='5'/></svg>"""
SVG_CHART = """<svg viewBox='0 0 64 64' fill='none' stroke='currentColor' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><path d='M10 52h44'/><rect x='15' y='32' width='7' height='16' rx='1' fill='currentColor' stroke='none'/><rect x='29' y='22' width='7' height='26' rx='1' fill='currentColor' stroke='none'/><rect x='43' y='13' width='7' height='35' rx='1' fill='currentColor' stroke='none'/></svg>"""
SVG_DROP = """<svg viewBox='0 0 64 64' fill='currentColor'><path d='M32 6C24 19 16 29 16 40a16 16 0 1 0 32 0C48 29 40 19 32 6Z'/><path d='M23 41c0 6 4 10 9 11' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' opacity='.55'/></svg>"""
SVG_DNA = """<svg viewBox='0 0 64 64' fill='none' stroke='currentColor' stroke-width='3' stroke-linecap='round'><path d='M20 8c0 18 24 18 24 36 0 6-3 10-5 12M44 8c0 18-24 18-24 36 0 6 3 10 5 12'/><path d='M22 15h20M25 25h14M25 39h14M22 49h20'/></svg>"""
SVG_LAPTOP = """<svg viewBox='0 0 64 64' fill='none' stroke='currentColor' stroke-width='3' stroke-linejoin='round'><rect x='12' y='10' width='40' height='30' rx='2'/><path d='M7 47h50l-4 7H11l-4-7Z'/><path d='M20 34V25M28 34V19M36 34V28M44 34V15' stroke-width='4'/></svg>"""
SVG_SHIELD = """<svg viewBox='0 0 64 64' fill='none' stroke='currentColor' stroke-width='3.2' stroke-linecap='round' stroke-linejoin='round'><path d='M32 7 49 14v14c0 12-7 22-17 29-10-7-17-17-17-29V14L32 7Z'/><path d='m23 31 6 6 12-13'/></svg>"""
SVG_PEOPLE = """<svg viewBox='0 0 64 64' fill='currentColor'><circle cx='32' cy='19' r='8'/><circle cx='15' cy='24' r='6'/><circle cx='49' cy='24' r='6'/><path d='M20 49c0-9 5-15 12-15s12 6 12 15v5H20v-5ZM4 53v-4c0-8 4-13 11-13 3 0 5 1 7 3-3 4-5 9-5 15H4ZM60 53v-4c0-8-4-13-11-13-3 0-5 1-7 3 3 4 5 9 5 15h13Z'/></svg>"""
SVG_ARROW = """<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'><path d='M5 12h13M14 7l5 5-5 5'/></svg>"""
SVG_MEGAPHONE = """<svg viewBox='0 0 64 64' fill='none' stroke='currentColor' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><path d='M11 29v9h9l23 10V19L20 29h-9Z'/><path d='M20 38 24 53h8l-5-12M49 24l6-5M50 34h8M49 44l6 5'/></svg>"""

pages = ["Home","AMBER Calculator","DNA Compass / Method","Model & Validation","About AMBER"]
page = st.segmented_control("Navigation", pages, default="Home", label_visibility="collapsed") or "Home"

if page == "Home":
    st.markdown(f'''
    <div class="home-title-row">
      <div class="home-title-left">
        <div class="home-kicker">RESEARCH CONCEPT</div>
        <div class="home-title">Why AMBER, and how does it work?</div>
        <div class="home-sub">From blood-based molecular measurement to a future estimate of cerebral amyloid positivity.</div>
      </div>
      <div class="home-brand-message">
        <div class="home-brand-main">BLOOD&nbsp;&nbsp;×&nbsp;&nbsp;<span class="home-brand-ai">AI</span>&nbsp;&nbsp;×&nbsp;&nbsp;BRAIN HEALTH</div>
        <div class="home-brand-sub">TRANSPARENT · REPRODUCIBLE · FOR A BRIGHTER TOMORROW</div>
      </div>
    </div>
    <div class="home-question">
      <div class="home-qicon">?</div><div class="home-qsep"></div>
      <div class="home-qcopy"><div class="home-qlabel">MAIN SCIENTIFIC QUESTION</div><div class="home-qtext">Can simultaneous blood-based measurement of Aβ40 and Aβ42, enabled by a programmable DNA Compass assay, support a transparent and eventually validated estimate of PET-defined cerebral amyloid positivity?</div></div>
    </div>
    <div class="home-section-title">Why this project matters</div>
    <div class="home-matters">
      <div class="home-matter-card"><div class="home-icon-disc">{SVG_BRAIN}</div><div><div class="home-matter-title">Imaging-defined pathology</div><div class="home-matter-body">Amyloid PET can define cerebral amyloid pathology.</div></div></div>
      <div class="home-matter-card amber"><div class="home-icon-disc">{SVG_TUBES}</div><div><div class="home-matter-title">Two related biomarkers</div><div class="home-matter-body">Aβ40 and Aβ42 are highly related peptides.</div></div></div>
      <div class="home-matter-card"><div class="home-icon-disc">{SVG_CHART}</div><div><div class="home-matter-title">Translation gap</div><div class="home-matter-body">A molecular measurement is useful only if it can be linked to a transparent, calibrated and externally validated pathology estimate.</div></div></div>
    </div>
    <div class="home-section-title path">AMBER research pathway</div>
    <div class="home-pathway">
      <div class="home-path-card"><div class="home-step-num">1</div><div class="home-path-icon red">{SVG_DROP}</div><div class="home-path-title">Measure</div><div class="home-path-body">Quantify plasma Aβ40 and Aβ42 using the DNA Compass workflow.</div></div><div class="home-path-arrow">{SVG_ARROW}</div>
      <div class="home-path-card"><div class="home-step-num">2</div><div class="home-path-icon">{SVG_DNA}</div><div class="home-path-title">Transform</div><div class="home-path-body">Derive Aβ42/Aβ40 and interpretable (R) and (M) terms.</div></div><div class="home-path-arrow">{SVG_ARROW}</div>
      <div class="home-path-card"><div class="home-step-num">3</div><div class="home-path-icon">{SVG_LAPTOP}</div><div class="home-path-title">Model</div><div class="home-path-body">Compare ratio-only, AMBER-B, and AMBER-C models.</div></div><div class="home-path-arrow">{SVG_ARROW}</div>
      <div class="home-path-card"><div class="home-step-num">4</div><div class="home-path-icon">{SVG_SHIELD}</div><div class="home-path-title">Validate</div><div class="home-path-body">Use PET-linked hospital data for discrimination, calibration and clinical-utility analysis.</div></div><div class="home-path-arrow">{SVG_ARROW}</div>
      <div class="home-path-card"><div class="home-step-num">5</div><div class="home-path-icon">{SVG_PEOPLE}</div><div class="home-path-title">Translate</div><div class="home-path-body">Load only a locked, validated model into the future AMBER production interface.</div></div>
    </div>
    <div class="home-stage"><div class="home-stage-icon">{SVG_MEGAPHONE}</div><div><strong>Current stage:</strong> AMBER V0.1 demonstrates the scientific and software architecture only. Clinical coefficients, thresholds and performance claims will be added only after real PET-linked data are analysed.</div></div>
    ''', unsafe_allow_html=True)

elif page == "AMBER Calculator":
    st.markdown('''
    <div class="calc-page-title-row">
      <div class="calc-page-title-left">
        <div class="calc-page-kicker">CORE COMPUTATIONAL INTERFACE</div>
        <div class="calc-page-title">AMBER Calculator</div>
      </div>
      <div class="calc-brand-message">
        <div class="calc-brand-main">BLOOD&nbsp;&nbsp;×&nbsp;&nbsp;<span class="calc-brand-ai">AI</span>&nbsp;&nbsp;×&nbsp;&nbsp;BRAIN HEALTH</div>
        <div class="calc-brand-sub">TRANSPARENT · REPRODUCIBLE · FOR A BRIGHTER TOMORROW</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.10, 1], gap="small")

    with c1:
        with st.container(border=False, key="amber_input_panel"):
            st.markdown('''<div class="calc-panel-head"><div class="calc-panel-num">1</div><div><div class="calc-panel-title">Input values</div><div class="calc-panel-sub">Enter biomarker values and, for AMBER-C, demographic variables.</div></div></div>''', unsafe_allow_html=True)
            with st.form("amber_form_locked"):
                st.markdown('<div class="calc-section-label">Model configuration</div>', unsafe_allow_html=True)
                model_name = st.selectbox("Model configuration", ["AMBER-B (biomarker-only)", "AMBER-C (biomarker + age/sex)"], label_visibility="collapsed")
                amber_b = model_name.startswith("AMBER-B")
                if not amber_b:
                    age = st.number_input("Age (years)", 18, 100, 68)
                    sex = st.radio("Sex", ["Male", "Female"], horizontal=True, index=1)
                else:
                    age = 68; sex = "Female"
                st.markdown('<div class="calc-biomarker-title">Biomarker measurements</div>', unsafe_allow_html=True)
                ab40 = st.number_input("Plasma Aβ40 concentration (pg/mL)", min_value=.01, value=285.0, step=1.0, format="%.2f")
                ab42 = st.number_input("Plasma Aβ42 concentration (pg/mL)", min_value=.01, value=18.5, step=.1, format="%.2f")
                demo = st.checkbox("Use illustrative demo probability", value=False, help="Uses placeholder coefficients only to demonstrate the software workflow.")
                submitted = st.form_submit_button("CALCULATE AMBER SCORE", use_container_width=True)
            st.markdown(f'''<div class="calc-info-callout"><div class="calc-info-icon">{SVG_CALC_INFO}</div><div>The calculation is performed only after you click<br><b>“Calculate AMBER Score”.</b></div></div>''', unsafe_allow_html=True)
            if submitted:
                ratio, R, M = derive(ab40, ab42); score = None
                if demo: ratio, R, M, score = demo_predict(model_name, ab40, ab42, age, sex)
                st.session_state.amber_result = {"model": model_name, "ratio": ratio, "R": R, "M": M, "score": score, "demo": demo}
                st.session_state.amber_report = {"application":APP_VERSION,"generated_at":datetime.now().isoformat(timespec="minutes"),"configuration":model_name,"inputs":{"ab40_pg_ml":ab40,"ab42_pg_ml":ab42,"age":None if amber_b else age,"sex":None if amber_b else sex},"derived":{"ratio":ratio,"R":R,"M":M},"illustrative_score":score,"status":"DEMONSTRATION ONLY" if demo else "DERIVED FEATURES ONLY"}

    with c2:
        with st.container(border=False, key="amber_results_panel"):
            st.markdown('''<div class="calc-panel-head"><div class="calc-panel-num">2</div><div><div class="calc-panel-title">Results</div><div class="calc-panel-sub">Illustrative output based on the current inputs.</div></div></div>''', unsafe_allow_html=True)
            r = st.session_state.amber_result
            if r is None:
                st.markdown('''<div style="height:405px;display:flex;align-items:center;justify-content:center;text-align:center;color:#6A7F97;font-size:13px;line-height:1.5"><div>Enter values in the Input panel and click<br><b style="color:#06285F">CALCULATE AMBER SCORE</b>.</div></div>''', unsafe_allow_html=True)
            else:
                if r["score"] is not None:
                    st.markdown(segmented_gauge_html(r["score"]), unsafe_allow_html=True)
                else:
                    st.markdown('''<div style="height:208px;display:flex;align-items:center;justify-content:center;text-align:center;color:#6A7F97;font-size:13px;line-height:1.5"><div><b style="color:#06285F">Derived biomarker features calculated.</b><br>No validated probability model is loaded.</div></div>''', unsafe_allow_html=True)
                st.markdown(f'''<div class="calc-metrics"><div class="calc-metric"><div class="calc-metric-label">Aβ42/Aβ40</div><div class="calc-metric-value">{r["ratio"]:.4f}</div></div><div class="calc-metric"><div class="calc-metric-label">R</div><div class="calc-metric-value">{r["R"]:.3f}</div></div><div class="calc-metric"><div class="calc-metric-label">M</div><div class="calc-metric-value">{r["M"]:.3f}</div></div></div>''', unsafe_allow_html=True)
                if r["demo"]:
                    st.markdown(f'''<div class="calc-demo-alert"><div class="calc-warning-icon">{SVG_WARNING_TRI}</div><div><div class="calc-demo-title">DEMONSTRATION OUTPUT ONLY.</div><div class="calc-demo-copy">Placeholder coefficients are used only to demonstrate the interface. This is not a clinically validated AMBER result.</div></div></div>''', unsafe_allow_html=True)
                if st.session_state.amber_report is not None:
                    pdf_bytes = build_amber_pdf(st.session_state.amber_report)
                    st.download_button("Download results summary (PDF)", data=pdf_bytes, file_name="AMBER_V01_results_summary.pdf", mime="application/pdf", use_container_width=True, key="amber_pdf_download")

    with c3:
        with st.container(border=False, key="amber_scientific_panel"):
            st.markdown('''<div class="calc-panel-head"><div class="calc-panel-num">3</div><div><div class="calc-panel-title">Scientific basis</div><div class="calc-science-intro">AMBER is designed to translate jointly measured Aβ40 and Aβ42 into a future calibrated probability of cerebral amyloid positivity.</div></div></div><div class="calc-divider"></div><div class="calc-science-heading">Feature definitions</div>''', unsafe_allow_html=True)
            st.latex(r"R=\log_{10}\left(\frac{A\beta42}{A\beta40}\right)")
            st.latex(r"M=\log_{10}\left(\sqrt{A\beta40\times A\beta42}\right)")
            st.markdown('<div class="calc-divider"></div><div class="calc-science-heading">AMBER-B (biomarker-only)</div>', unsafe_allow_html=True)
            st.latex(r"I_B=\beta_0+\beta_RR+\beta_MM")
            st.markdown('<div class="calc-science-heading" style="margin-top:3px">AMBER-C (with demographics)</div>', unsafe_allow_html=True)
            st.latex(r"I_C=\beta_0+\beta_RR+\beta_MM+\beta_AAge+\beta_SSex")
            st.markdown('<div class="calc-science-heading" style="margin-top:3px">Probability (both models)</div>', unsafe_allow_html=True)
            st.latex(r"P=\frac{1}{1+e^{-I}}")
            st.markdown(f'''<div class="calc-safeguard"><div class="calc-bulb">{SVG_BULB}</div><div><b>Scientific safeguard:</b> no final β coefficients, clinical thresholds, AUC, sensitivity, specificity, or model-lock date are shown until they are empirically derived and validated.</div></div>''', unsafe_allow_html=True)

    st.markdown(f'''<div class="calc-workflow"><div class="calc-workflow-intro"><div class="calc-workflow-title">What happens after you click Calculate?</div><div class="calc-workflow-sub">From input to AMBER score in four steps.</div></div><div class="calc-workflow-sep"></div><div class="calc-workflow-steps"><div class="calc-work-step"><div class="calc-work-num">1</div><div class="calc-work-icon">{SVG_CLIPBOARD}</div><div><div class="calc-work-title">Read inputs</div><div class="calc-work-copy">Get biomarker (and<br>demographic) values.</div></div></div><div class="calc-work-arrow">{SVG_ARROW}</div><div class="calc-work-step"><div class="calc-work-num">2</div><div class="calc-work-icon">{SVG_GEAR}</div><div><div class="calc-work-title">Derive features</div><div class="calc-work-copy">Compute ratio (R)<br>and geometric mean (M).</div></div></div><div class="calc-work-arrow">{SVG_ARROW}</div><div class="calc-work-step"><div class="calc-work-num">3</div><div class="calc-work-icon">{SVG_CHART}</div><div><div class="calc-work-title">Apply model</div><div class="calc-work-copy">Calculate I and convert<br>to probability.</div></div></div><div class="calc-work-arrow">{SVG_ARROW}</div><div class="calc-work-step"><div class="calc-work-num">4</div><div class="calc-work-icon">{SVG_REPORT}</div><div><div class="calc-work-title">Report</div><div class="calc-work-copy">Display score and<br>summary outputs.</div></div></div></div></div>''', unsafe_allow_html=True)
    st.markdown('<style>.footer{height:28px!important;margin-top:0!important;padding-top:8px!important}</style>', unsafe_allow_html=True)

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

footer_class = "footer home-footer" if page == "Home" else "footer"
st.markdown(f'<div class="{footer_class}"><div><b>{APP_VERSION}</b></div><div>Model status: {MODEL_STATUS}</div><div>Research use only · Not a diagnostic test</div></div>', unsafe_allow_html=True)
