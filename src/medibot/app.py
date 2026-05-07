"""Streamlit web interface for MediBot -- Premium Landing + Chat UI."""

import logging

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from medibot.llm import build_rag_chain
from medibot.vectorstore import load_vectorstore

import html
import markdown as _md

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---- Premium CSS --------------------------------------------
_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  @keyframes _pulse{0%,100%{opacity:1}50%{opacity:.4}}
  @keyframes _fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
  @keyframes _glowPulse{0%,100%{box-shadow:0 0 14px rgba(37,99,235,.3)}50%{box-shadow:0 0 28px rgba(37,99,235,.5)}}

  .stApp{background:#0a0f1e!important;font-family:'Inter',system-ui,sans-serif!important}
  #MainMenu,footer,header,.stDecoration,.stAppDeployButton{display:none!important}
  .main .block-container{padding:0 16px!important;max-width:820px!important;margin:0 auto!important;}
  [data-testid="stSidebar"]{display:none!important}
  ::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:rgba(255,255,255,.06);border-radius:3px}

  .stApp::before{
    content:'';position:fixed;inset:0;z-index:-1;
    background:radial-gradient(ellipse 70% 50% at 50% 30%,rgba(37,99,235,.06),transparent 70%),
      radial-gradient(ellipse 40% 40% at 10% 80%,rgba(6,182,212,.04),transparent 60%),
      radial-gradient(ellipse 40% 40% at 90% 80%,rgba(139,92,246,.03),transparent 60%);
    pointer-events:none;
  }
  .stApp::after{
    content:'';position:fixed;inset:0;z-index:-1;
    background-image:linear-gradient(rgba(255,255,255,.012) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.012) 1px,transparent 1px);
    background-size:64px 64px;pointer-events:none;
  }

  /* ---- Landing buttons ---- */
  .stButton>button{
    background:transparent!important;border:1px solid rgba(255,255,255,.08)!important;
    color:#cbd5e1!important;border-radius:12px!important;font-family:'Inter',sans-serif!important;
    font-weight:500!important;transition:all .25s ease!important;
  }
  .stButton>button:hover{background:rgba(255,255,255,.06)!important;border-color:#3b82f6!important;color:#fff!important;transform:translateY(-1px)!important}
  .stButton>button[kind="primary"]{
    background:linear-gradient(135deg,#2563eb,#3b82f6)!important;border:none!important;
    color:#fff!important;font-weight:600!important;letter-spacing:.3px!important;
    box-shadow:0 4px 24px rgba(37,99,235,.35)!important;
  }
  .stButton>button[kind="primary"]:hover{box-shadow:0 8px 40px rgba(37,99,235,.5)!important;transform:translateY(-2px)!important}

  /* ========== CHAT NAVBAR ========== */
  .chat-navbar{
    display:flex;justify-content:space-between;align-items:center;
    padding:8px 0 4px;flex-shrink:0;gap:12px;
  }
  .chat-navbar .stButton>button{
    background:rgba(255,255,255,.04)!important;backdrop-filter:blur(12px)!important;
    border:1px solid rgba(255,255,255,.08)!important;border-radius:10px!important;
    padding:7px 14px 7px 10px!important;color:#94a3b8!important;
    font-size:13px!important;font-weight:500!important;
    width:auto!important;transition:all .3s ease!important;
    display:inline-flex!important;align-items:center!important;gap:6px!important;
  }
  .chat-navbar .stButton>button:hover{
    background:rgba(255,255,255,.08)!important;border-color:rgba(59,130,246,.25)!important;
    color:#f1f5f9!important;transform:translateX(-2px)!important;
  }
  .chat-nav-brand{
    display:flex;align-items:center;gap:10px;
  }
  .chat-nav-brand-text{font-size:15px;font-weight:700;color:#f1f5f9;}
  .chat-nav-badge{
    font-size:9px;font-weight:600;color:#22d3ee;
    padding:3px 10px;background:rgba(6,182,212,.1);
    border:1px solid rgba(6,182,212,.15);border-radius:100px;
    letter-spacing:.3px;text-transform:uppercase;
  }
  .chat-nav-status{
    display:flex;align-items:center;gap:5px;
    font-size:11px;color:#22c55e;font-weight:500;
  }
  .chat-nav-dot{
    width:6px;height:6px;border-radius:50%;background:#22c55e;
    box-shadow:0 0 8px rgba(34,197,94,.5);animation:_pulse 2.5s ease-in-out infinite;
  }

  /* ========== CHAT MESSAGES ========== */
  .chat-msgs{
    flex:1;overflow-y:auto;padding:4px 0 12px;
    display:flex;flex-direction:column;gap:4px;
    min-height:0;
  }

  /* ========== MESSAGE ROWS ========== */
  .chat-row{
    display:flex;align-items:flex-end;gap:10px;
    width:100%;animation:_fadeIn .3s ease;
    padding:2px 0;
  }
  .chat-row.user-row{justify-content:flex-end;}
  .chat-row.bot-row{justify-content:flex-start;}

  /* ========== AVATARS ========== */
  .chat-avatar{
    width:30px;height:30px;border-radius:8px;
    flex-shrink:0;overflow:hidden;display:flex;
    align-items:center;justify-content:center;
  }
  .chat-avatar svg{width:100%;height:100%;display:block;}
  .chat-avatar.bot{
    background:linear-gradient(135deg,#2563eb,#06b6d4);
    box-shadow:0 0 12px rgba(37,99,235,.2);
  }
  .chat-avatar.user{
    background:#1e293b;border:1px solid rgba(255,255,255,.06);
  }

  /* ========== BUBBLES ========== */
  .chat-bubble{
    max-width:75%;padding:11px 16px;
    font-size:14px;line-height:1.65;
    word-wrap:break-word;position:relative;
  }
  .chat-bubble.bot{
    max-width:72%;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.06);
    color:#e2e8f0;border-radius:4px 16px 16px 16px;
  }
  .chat-bubble.user{
    max-width:60%;
    background:linear-gradient(135deg,#1a365d,#1e3a5f);
    border:1px solid rgba(59,130,246,.15);
    color:#f1f5f9;border-radius:16px 4px 16px 16px;
    text-align:left;
  }
  .chat-time{
    font-size:10px;color:rgba(148,163,184,.35);
    margin-top:5px;letter-spacing:.2px;
  }
  .chat-row.user-row .chat-time{text-align:right;}
  .chat-row.bot-row .chat-time{text-align:left;}

  /* ========== MARKDOWN CONTENT ========== */
  .chat-content > :first-child{margin-top:0;}
  .chat-content > :last-child{margin-bottom:0;}
  .chat-content h1,.chat-content h2,.chat-content h3,.chat-content h4{
    margin:14px 0 6px;color:#f1f5f9;font-weight:700;line-height:1.3;
  }
  .chat-content h1{font-size:17px;}
  .chat-content h2{font-size:16px;}
  .chat-content h3{font-size:15px;}
  .chat-content h4{font-size:14px;}
  .chat-content p{margin:7px 0;color:#e2e8f0;}
  .chat-content ul,.chat-content ol{margin:6px 0;padding-left:20px;color:#e2e8f0;}
  .chat-content li{margin:3px 0;line-height:1.55;}
  .chat-content strong{color:#f1f5f9;font-weight:600;}
  .chat-content em{color:#cbd5e1;}
  .chat-content code{
    background:rgba(255,255,255,.06);padding:1px 5px;border-radius:3px;
    font-size:13px;color:#22d3ee;
  }
  .chat-content pre{
    background:rgba(0,0,0,.3);padding:10px 14px;border-radius:8px;
    overflow-x:auto;margin:8px 0;
  }
  .chat-content pre code{background:none;padding:0;color:#e2e8f0;}
  .chat-content blockquote{
    border-left:2px solid rgba(59,130,246,.3);padding-left:12px;
    margin:8px 0;color:#94a3b8;font-style:italic;
  }
  .chat-cursor{animation:_pulse 1.2s ease-in-out infinite;opacity:.5;}

  /* ========== SOURCES ========== */
  .chat-srcs{margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,.05);}
  .chat-srcs summary{
    font-size:11px;color:#64748b;cursor:pointer;font-weight:500;letter-spacing:.3px;
  }
  .chat-srcs summary:hover{color:#94a3b8;}
  .chat-srcs-list{padding:6px 0 0;margin:0;list-style:none;}
  .chat-srcs-list li{
    font-size:11.5px;color:#64748b;padding:4px 0;
    border-bottom:1px solid rgba(255,255,255,.02);line-height:1.5;
  }
  .chat-srcs-list li:last-child{border-bottom:none;}
  .chat-srcs-list strong{color:#94a3b8;}

  /* ========== FEEDBACK ========== */
  .chat-fb{display:flex;gap:4px;margin-top:6px;}
  .chat-fb button{
    background:none;border:1px solid rgba(255,255,255,.05);
    border-radius:5px;padding:3px 7px;cursor:pointer;
    color:#475569;font-size:11px;transition:all .2s;
  }
  .chat-fb button:hover{background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.1);color:#94a3b8;}

  /* ========== WELCOME ========== */
  .chat-welcome{
    flex:1;display:flex;flex-direction:column;
    align-items:center;justify-content:center;
    text-align:center;padding:16px 20px;gap:12px;
    animation:_fadeIn .6s ease;
  }
  .chat-welcome-icon{
    width:64px;height:64px;border-radius:16px;
    background:linear-gradient(135deg,rgba(37,99,235,.12),rgba(6,182,212,.08));
    border:1px solid rgba(37,99,235,.12);
    display:flex;align-items:center;justify-content:center;
  }
  .chat-welcome-icon svg{width:32px;height:32px;}
  .chat-welcome-title{font-size:19px;font-weight:700;color:#f1f5f9;letter-spacing:-.3px;}
  .chat-welcome-sub{font-size:13.5px;color:#64748b;max-width:320px;line-height:1.6;}

  /* ========== DISCLAIMER ========== */
  .chat-disc{
    font-size:10.5px;color:rgba(71,85,105,.45);
    text-align:center;padding:4px 16px 0;line-height:1.4;
    flex-shrink:0;
  }

  /* ========== CHAT INPUT ========== */
  [data-testid="stChatInput"]{
    position:sticky!important;bottom:0!important;
    padding:6px 0 10px!important;
    background:linear-gradient(180deg,transparent,#0a0f1e 30%)!important;
    border:none!important;flex-shrink:0!important;
  }
  [data-testid="stChatInput"] > div{
    display:flex;align-items:center;gap:8px;
    background:rgba(255,255,255,.04)!important;
    border:1px solid rgba(255,255,255,.08)!important;
    border-radius:14px!important;padding:4px!important;
    transition:border-color .25s ease,box-shadow .25s ease!important;
  }
  [data-testid="stChatInput"] > div:focus-within{
    border-color:rgba(59,130,246,.3)!important;
    box-shadow:0 0 0 3px rgba(59,130,246,.1)!important;
  }
  [data-testid="stChatInput"] textarea{
    background:transparent!important;border:none!important;
    padding:9px 12px!important;font-size:14px!important;
    color:#f1f5f9!important;font-family:'Inter',sans-serif!important;
    outline:none!important;resize:none!important;
    line-height:1.5!important;min-height:20px!important;
  }
  [data-testid="stChatInput"] textarea::placeholder{color:#475569!important;}
  [data-testid="stChatInput"] button{
    width:36px!important;height:36px!important;border-radius:10px!important;
    background:linear-gradient(135deg,#2563eb,#3b82f6)!important;
    border:none!important;cursor:pointer!important;
    display:flex!important;align-items:center!important;justify-content:center!important;
    transition:all .25s ease!important;flex-shrink:0!important;padding:0!important;
  }
  [data-testid="stChatInput"] button:hover{transform:scale(1.05)!important;}
  [data-testid="stChatInput"] button svg{width:17px;height:17px;display:block;}
  [data-testid="stChatInput"] button p{display:none!important;}

  /* ========== RESPONSIVE ========== */
  @media(max-width:768px){
    .main .block-container{padding:0 10px!important;}
    .chat-bubble.chat-bubble{max-width:82%;padding:10px 14px;font-size:13.5px;}
    .chat-avatar{width:28px;height:28px;}
    .chat-welcome-icon{width:56px;height:56px;}
    .chat-welcome-icon svg{width:28px;height:28px;}
    .chat-welcome-title{font-size:17px;}
  }
  @media(max-width:480px){
    .main .block-container{padding:0 6px!important;}
    .chat-bubble.chat-bubble{max-width:88%;padding:9px 12px;font-size:13px;}
    .chat-avatar{width:24px;height:24px;}
    .chat-navbar{flex-wrap:wrap;gap:8px;}
    .chat-nav-brand-text{font-size:14px;}
    .chat-nav-badge{font-size:8px;padding:2px 8px;}
  }
</style>
"""


# ==============================================================================
#  LANDING PAGE
# ==============================================================================
def render_landing():
    # ========================= HERO =========================
    st.markdown("""
<div style="position:relative;min-height:90vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:60px 24px 40px;overflow:hidden;
  background:
    radial-gradient(ellipse 70% 55% at 50% 40%, rgba(37,99,235,.08), transparent 70%),
    radial-gradient(ellipse 50% 40% at 20% 80%, rgba(6,182,212,.05), transparent 55%),
    radial-gradient(ellipse 50% 40% at 80% 20%, rgba(139,92,246,.04), transparent 55%);">
  <div style="position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.015) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.015) 1px,transparent 1px);background-size:60px 60px;-webkit-mask-image:radial-gradient(ellipse 60% 50% at 50% 50%,black 25%,transparent 100%);pointer-events:none;"></div>
  <div style="position:absolute;width:400px;height:400px;background:#2563eb;border-radius:50%;filter:blur(120px);opacity:.08;top:5%;left:5%;pointer-events:none;animation:_float 12s ease-in-out infinite;"></div>
  <div style="position:absolute;width:300px;height:300px;background:#06b6d4;border-radius:50%;filter:blur(120px);opacity:.06;top:20%;right:10%;pointer-events:none;animation:_float 12s ease-in-out infinite 4s;"></div>
  <div style="position:absolute;width:200px;height:200px;background:#8b5cf6;border-radius:50%;filter:blur(100px);opacity:.05;bottom:15%;left:40%;pointer-events:none;animation:_float 12s ease-in-out infinite 8s;"></div>

  <div style="position:relative;z-index:2;display:inline-flex;align-items:center;gap:8px;padding:7px 16px 7px 14px;background:rgba(6,182,212,.07);border:1px solid rgba(6,182,212,.15);border-radius:100px;font-size:12px;font-weight:500;color:#22d3ee;margin-bottom:36px;letter-spacing:.2px;">
    <span style="width:6px;height:6px;background:#22d3ee;border-radius:50%;box-shadow:0 0 10px #22d3ee;animation:_pulse 2s ease-in-out infinite;"></span>
    Powered by RAG + LLM
  </div>

  <h1 style="position:relative;z-index:2;font-family:'Inter',sans-serif;font-size:clamp(42px,7vw,80px);font-weight:900;letter-spacing:-3px;line-height:1.05;margin:0 0 20px;color:#f1f5f9;">
    Medi<span style="background:linear-gradient(135deg,#3b82f6,#06b6d4,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Bot</span>
  </h1>

  <p style="position:relative;z-index:2;font-size:clamp(15px,2vw,18px);font-weight:400;color:#94a3b8;max-width:500px;margin:0 auto;line-height:1.7;">
    Your AI-Powered Medical Reference Assistant. Ask questions and get answers grounded in verified clinical literature.
  </p>

  <div style="position:absolute;bottom:28px;left:50%;transform:translateX(-50%);z-index:2;display:flex;flex-direction:column;align-items:center;gap:4px;opacity:.2;">
    <span style="font-size:10px;color:#64748b;letter-spacing:2px;text-transform:uppercase;">Scroll</span>
    <div style="width:16px;height:26px;border:2px solid #64748b;border-radius:8px;position:relative;">
      <div style="position:absolute;top:5px;left:50%;transform:translateX(-50%);width:2px;height:5px;background:#64748b;border-radius:2px;animation:_pulse 2s ease-in-out infinite;"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2.5, 1])
    with c2:
        if st.button("Get Started \u2192", type="primary", use_container_width=True, key="cta_start"):
            st.session_state.page = "chat"
            st.rerun()

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.06),transparent);max-width:900px;margin:0 auto;"></div>', unsafe_allow_html=True)

    # ========================= STATS =========================
    st.markdown("""
<div class="_resp-grid" style="max-width:900px;margin:0 auto;padding:60px 24px;display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);border-radius:16px;">
  <div style="text-align:center;padding:24px 16px;border-right:1px solid rgba(255,255,255,.05);">
    <p style="font-size:clamp(24px,3vw,32px);font-weight:800;margin:0;background:linear-gradient(135deg,#3b82f6,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">10K+</p>
    <p style="font-size:13px;color:#64748b;margin:6px 0 0;">Medical References</p>
  </div>
  <div style="text-align:center;padding:24px 16px;border-right:1px solid rgba(255,255,255,.05);">
    <p style="font-size:clamp(24px,3vw,32px);font-weight:800;margin:0;background:linear-gradient(135deg,#3b82f6,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">&lt;3s</p>
    <p style="font-size:13px;color:#64748b;margin:6px 0 0;">Avg. Response Time</p>
  </div>
  <div style="text-align:center;padding:24px 16px;">
    <p style="font-size:clamp(24px,3vw,32px);font-weight:800;margin:0;background:linear-gradient(135deg,#3b82f6,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">100%</p>
    <p style="font-size:13px;color:#64748b;margin:6px 0 0;">Source Cited</p>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.06),transparent);max-width:900px;margin:0 auto;"></div>', unsafe_allow_html=True)

    # ========================= FEATURES =========================
    st.markdown("""
<div style="max-width:900px;margin:0 auto;text-align:center;padding:80px 24px 20px;">
  <div style="display:inline-flex;align-items:center;gap:6px;padding:5px 14px;background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.15);border-radius:100px;font-size:11px;font-weight:600;color:#60a5fa;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;">Features</div>
  <h2 style="font-family:'Inter',sans-serif;font-size:clamp(26px,3.5vw,36px);font-weight:800;color:#f1f5f9;letter-spacing:-1px;margin:0 0 10px;">Why MediBot?</h2>
  <p style="font-size:15px;color:#64748b;max-width:460px;margin:0 auto;line-height:1.65;">Built for medical professionals, students, and anyone who needs reliable, sourced medical information.</p>
</div>
""", unsafe_allow_html=True)

    cards = [
        ("\U0001f52c", "rgba(59,130,246,.12)", "rgba(59,130,246,.25)", "RAG-Powered Accuracy", "Answers grounded in verified medical literature, not hallucinations."),
        ("\u26a1", "rgba(6,182,212,.12)", "rgba(6,182,212,.25)", "Instant Responses", "Get precise answers in seconds with ultra-fast inference."),
        ("\U0001f6e1\ufe0f", "rgba(139,92,246,.12)", "rgba(139,92,246,.25)", "Safe & Reliable", "Built with responsible AI practices and built-in disclaimers."),
        ("\U0001f4da", "rgba(16,185,129,.12)", "rgba(16,185,129,.25)", "Medical Knowledge Base", "Search across thousands of clinical references and documents."),
        ("\U0001f4ac", "rgba(245,158,11,.12)", "rgba(245,158,11,.25)", "Conversational AI", "Natural dialogue with full context awareness across conversations."),
        ("\U0001f4c4", "rgba(244,63,94,.12)", "rgba(244,63,94,.25)", "Source Citations", "Every answer includes references to the exact source documents."),
    ]

    for row in range(0, 6, 3):
        cols = st.columns(3, gap="medium")
        for i in range(3):
            idx = row + i
            icon, bg, border, title, desc = cards[idx]
            with cols[i]:
                st.markdown(f"""
<div style="background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:32px 24px 34px;margin:6px 0;cursor:default;transition:all .4s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden;" onmouseover="this.style.transform='translateY(-6px)';this.style.borderColor='rgba(59,130,246,.3)';this.style.boxShadow='0 16px 48px rgba(0,0,0,.35),0 0 0 1px rgba(59,130,246,.08)';this.style.background='rgba(255,255,255,.035)';this.querySelector('._glow').style.opacity='1'" onmouseout="this.style.transform='translateY(0)';this.style.borderColor='rgba(255,255,255,.06)';this.style.boxShadow='none';this.style.background='rgba(255,255,255,.02)';this.querySelector('._glow').style.opacity='0'">
  <div class="_glow" style="position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 50% 50%,rgba(59,130,246,.04),transparent 60%);opacity:0;transition:opacity .6s ease;pointer-events:none;"></div>
  <div style="position:relative;z-index:1;width:46px;height:46px;display:flex;align-items:center;justify-content:center;background:{bg};border:1px solid {border};border-radius:12px;font-size:20px;margin-bottom:18px;transition:transform .4s ease;" onmouseover="this.style.transform='scale(1.08)'" onmouseout="this.style.transform='scale(1)'">{icon}</div>
  <h3 style="position:relative;z-index:1;font-family:'Inter',sans-serif;font-size:16px;font-weight:700;color:#f1f5f9;margin:0 0 8px;">{title}</h3>
  <p style="position:relative;z-index:1;font-size:13.5px;color:#64748b;line-height:1.65;margin:0;">{desc}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.06),transparent);max-width:900px;margin:0 auto;"></div>', unsafe_allow_html=True)

    # ========================= HOW IT WORKS =========================
    st.markdown("""
<div style="max-width:900px;margin:0 auto;text-align:center;padding:80px 24px 20px;">
  <div style="display:inline-flex;align-items:center;gap:6px;padding:5px 14px;background:rgba(6,182,212,.08);border:1px solid rgba(6,182,212,.15);border-radius:100px;font-size:11px;font-weight:600;color:#22d3ee;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;">Process</div>
  <h2 style="font-family:'Inter',sans-serif;font-size:clamp(26px,3.5vw,36px);font-weight:800;color:#f1f5f9;letter-spacing:-1px;margin:0 0 10px;">How It Works</h2>
  <p style="font-size:15px;color:#64748b;max-width:440px;margin:0 auto;line-height:1.65;">Three simple steps to get medically-grounded answers.</p>
</div>
""", unsafe_allow_html=True)

    steps = [
        ("1", "Ask a Question", "Type any medical question or clinical scenario in natural language."),
        ("2", "Retrieve Context", "RAG finds the most relevant passages from your medical documents."),
        ("3", "Get Cited Answer", "AI synthesises a precise response with source citations."),
    ]
    cols = st.columns(3, gap="small")
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
<div style="text-align:center;padding:28px 20px 32px;margin:6px 0;cursor:default;transition:all .4s cubic-bezier(.4,0,.2,1);border-radius:16px;border:1px solid transparent;" onmouseover="this.style.transform='translateY(-4px)';this.style.borderColor='rgba(59,130,246,.12)';this.style.boxShadow='0 12px 36px rgba(0,0,0,.25)'" onmouseout="this.style.transform='translateY(0)';this.style.borderColor='transparent';this.style.boxShadow='none'">
  <div style="width:50px;height:50px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#2563eb,#3b82f6);border-radius:14px;font-size:19px;font-weight:800;color:#fff;margin:0 auto 16px;box-shadow:0 4px 20px rgba(37,99,235,.35);position:relative;transition:transform .4s ease,box-shadow .4s ease;" onmouseover="this.style.transform='scale(1.1)';this.style.boxShadow='0 6px 28px rgba(37,99,235,.5)'" onmouseout="this.style.transform='scale(1)';this.style.boxShadow='0 4px 20px rgba(37,99,235,.35)'">
    {num}
  </div>
  <h3 style="font-family:'Inter',sans-serif;font-size:17px;font-weight:700;color:#f1f5f9;margin:0 0 8px;">{title}</h3>
  <p style="font-size:13.5px;color:#64748b;line-height:1.65;margin:0 auto;max-width:250px;">{desc}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.06),transparent);max-width:900px;margin:0 auto;"></div>', unsafe_allow_html=True)

    # ========================= CTA BANNER =========================
    st.markdown("""
<div style="max-width:900px;margin:60px auto 40px;text-align:center;padding:50px 24px;background:linear-gradient(135deg,rgba(37,99,235,.06),rgba(6,182,212,.04));border:1px solid rgba(37,99,235,.12);border-radius:16px;position:relative;overflow:hidden;">
  <div style="position:absolute;width:200px;height:200px;background:#3b82f6;border-radius:50%;filter:blur(80px);opacity:.06;top:-50px;right:-50px;pointer-events:none;"></div>
  <div style="position:absolute;width:180px;height:180px;background:#06b6d4;border-radius:50%;filter:blur(80px);opacity:.05;bottom:-60px;left:-40px;pointer-events:none;"></div>
  <h2 style="font-family:'Inter',sans-serif;font-size:clamp(22px,3vw,30px);font-weight:800;color:#f1f5f9;margin:0 0 10px;letter-spacing:-.5px;position:relative;z-index:2;">Ready to get started?</h2>
  <p style="font-size:15px;color:#64748b;max-width:420px;margin:0 auto;line-height:1.6;position:relative;z-index:2;">Ask your first medical question and get a cited, accurate answer in seconds.</p>
</div>
""", unsafe_allow_html=True)

    # ========================= FOOTER =========================
    st.markdown("""
<div style="max-width:900px;margin:0 auto;padding:40px 24px 60px;display:flex;flex-direction:column;align-items:center;gap:10px;">
  <div style="display:flex;align-items:center;gap:8px;">
    <div style="width:26px;height:26px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#2563eb,#06b6d4);border-radius:6px;font-size:14px;font-weight:800;color:#fff;">M</div>
    <span style="font-size:14px;font-weight:700;color:#e2e8f0;">MediBot</span>
  </div>
  <p style="font-size:13px;color:#475569;margin:0;">Powered by <span style="color:#64748b;">RAG</span> + <span style="color:#64748b;">LLM</span></p>
  <p style="font-size:11.5px;color:rgba(71,85,105,.6);margin:2px 0 0;text-align:center;max-width:400px;line-height:1.5;">For reference only. Not a substitute for professional medical advice.</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
#  SVG ICONS
# ==============================================================================
_BOT_ICON = """<svg width="30" height="30" viewBox="0 0 30 30" fill="none"><rect width="30" height="30" rx="7" fill="url(#bi)"/><path d="M15 7a3 3 0 0 0-3 3v2h-2a3 3 0 0 0-3 3 3 3 0 0 0 3 3h2v2a3 3 0 0 0 3 3 3 3 0 0 0 3-3v-2h2a3 3 0 0 0 3-3 3 3 0 0 0-3-3h-2v-2a3 3 0 0 0-3-3z" fill="#fff" opacity=".9"/><circle cx="20" cy="20" r="4.5" fill="#22d3ee" opacity=".2"/><circle cx="21.5" cy="21.5" r="2" fill="#22d3ee" opacity=".3"/><defs><linearGradient id="bi" x1="0" y1="0" x2="30" y2="30"><stop stop-color="#2563eb"/><stop offset="1" stop-color="#06b6d4"/></linearGradient></defs></svg>"""

_USER_ICON = """<svg width="30" height="30" viewBox="0 0 30 30" fill="none"><rect width="30" height="30" rx="7" fill="#1e293b"/><circle cx="15" cy="10" r="4" fill="#475569"/><path d="M6 25c0-4.97 4.03-9 9-9s9 4.03 9 9" stroke="#475569" stroke-width="2.3" fill="none" stroke-linecap="round"/></svg>"""

_WELCOME_BOT = """<svg width="32" height="32" viewBox="0 0 30 30" fill="none"><rect width="30" height="30" rx="7" fill="url(#wi)"/><path d="M15 7a3 3 0 0 0-3 3v2h-2a3 3 0 0 0-3 3 3 3 0 0 0 3 3h2v2a3 3 0 0 0 3 3 3 3 0 0 0 3-3v-2h2a3 3 0 0 0 3-3 3 3 0 0 0-3-3h-2v-2a3 3 0 0 0-3-3z" fill="#fff" opacity=".9"/><defs><linearGradient id="wi" x1="0" y1="0" x2="30" y2="30"><stop stop-color="#2563eb"/><stop offset="1" stop-color="#06b6d4"/></linearGradient></defs></svg>"""


# ==============================================================================
#  MESSAGE HELPERS
# ==============================================================================
def _ts():
    from datetime import datetime
    return datetime.now().strftime("%I:%M %p")


def _md_to_html(text):
    return _md.markdown(text, extensions=["extra"], output_format="html5")


def render_user_message(content, ts=None):
    safe = html.escape(content)
    return f"""
<div class="chat-row user-row">
  <div class="chat-bubble user">
    <div>{safe}</div>
    <div class="chat-time">{ts or _ts()}</div>
  </div>
  <div class="chat-avatar user">{_USER_ICON}</div>
</div>"""


def render_assistant_message(content, sources=None, ts=None, fb_key=None, cursor=False, plain=False):
    src_html = ""
    if sources:
        items = "".join(
            f'<li><strong>[{i}] {d.metadata.get("source","Unknown")}:</strong> {d.page_content[:200].replace(chr(10)," ")}...</li>'
            for i, d in enumerate(sources, 1)
        )
        src_html = f'<details class="chat-srcs"><summary>Source Documents</summary><ul class="chat-srcs-list">{items}</ul></details>'
    fb_html = ""
    if fb_key:
        fb_html = '<div class="chat-fb"><button onclick="alert(\'Marked helpful\')" title="Helpful">+1</button><button onclick="alert(\'Flagged for review\')" title="Not helpful">-1</button></div>'
    display = content if plain else _md_to_html(content)
    cursor_html = '<span class="chat-cursor">&#x258c;</span>' if cursor else ""
    return f"""
<div class="chat-row bot-row">
  <div class="chat-avatar bot">{_BOT_ICON}</div>
  <div class="chat-bubble bot">
    <div class="chat-content">{display}{cursor_html}</div>
    {src_html}
    {fb_html}
    <div class="chat-time">{ts or _ts()}</div>
  </div>
</div>"""


# ==============================================================================
#  CHAT PAGE
# ==============================================================================
def render_chat():
    # ===================== NAVBAR =====================
    nav1, nav2 = st.columns([0.38, 0.62])
    with nav1:
        if st.button("\u2190  Back to Home", key="back_home_top"):
            st.session_state.page = "landing"
            st.rerun()
    with nav2:
        st.markdown(f"""
<div class="chat-nav-brand">
  <span class="chat-nav-brand-text">MediBot</span>
  <span class="chat-nav-badge">RAG + LLM</span>
  <span class="chat-nav-status"><span class="chat-nav-dot"></span>Online</span>
</div>
""", unsafe_allow_html=True)

    # ===================== MESSAGES =====================
    if "messages" not in st.session_state:
        st.session_state.messages = []
    msgs = st.session_state.messages

    def _build_msgs():
        parts = ['<div class="chat-msgs">']
        if not msgs:
            parts.append(f"""<div class="chat-welcome">
  <div class="chat-welcome-icon">{_WELCOME_BOT}</div>
  <div class="chat-welcome-title">How can I help you today?</div>
  <div class="chat-welcome-sub">Ask any medical question and get answers grounded in verified clinical literature.</div>
</div>""")
        else:
            for m in msgs:
                if m["role"] == "user":
                    parts.append(render_user_message(m["content"], m.get("ts")))
                else:
                    parts.append(render_assistant_message(m["content"], m.get("sources"), m.get("ts"), m.get("fb")))
        parts.append('</div>')
        return '\n'.join(parts)

    st.html(_build_msgs())

    # ===================== DISCLAIMER =====================
    st.html('<p class="chat-disc">Responses are for educational reference only. Not a substitute for professional medical advice.</p>')

    # ===================== INPUT =====================
    prompt = st.chat_input("Ask a medical question...", key="chat_input_main")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "ts": _ts()})
        st.rerun()

    # ===================== STREAMING =====================
    if msgs and msgs[-1]["role"] == "user":
        last_user = msgs[-1]["content"]
        ph = st.empty()
        ph.html(render_assistant_message('Thinking...', plain=True, cursor=True))
        try:
            rag_chain = get_rag_chain()
            chat_history = []
            for m in msgs[:-1]:
                if m["role"] == "user":
                    chat_history.append(HumanMessage(content=m["content"]))
                else:
                    chat_history.append(AIMessage(content=m["content"]))
            full, last = "", None
            for chunk in rag_chain.stream({"input": last_user, "chat_history": chat_history}):
                if "answer" in chunk:
                    full += chunk["answer"]
                    ph.html(render_assistant_message(full, cursor=True))
                last = chunk
            sources = last.get("context", []) if last else []
            ts = _ts()
            fb_key = f"fb_{len(msgs)}"
            ph.html(render_assistant_message(full, sources, ts, fb_key))
            msgs.append({
                "role": "assistant", "content": full, "sources": sources, "ts": ts, "fb": fb_key,
            })
            st.rerun()
        except Exception as e:
            ph.html(render_assistant_message(f'Error: {html.escape(str(e))}', plain=True))
            logger.exception("Query failed")


# ==============================================================================
#  RAG CHAIN (cached)
# ==============================================================================
@st.cache_resource
def get_rag_chain():
    vectorstore = load_vectorstore()
    return build_rag_chain(vectorstore)


# ==============================================================================
#  MAIN
# ==============================================================================
def main():
    st.set_page_config(page_title="MediBot", page_icon=":hospital:", layout="wide", initial_sidebar_state="collapsed")
    st.html(_CSS)

    if "chain_loaded" not in st.session_state:
        get_rag_chain()
        st.session_state.chain_loaded = True

    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.session_state.page == "landing":
        render_landing()
    else:
        render_chat()


if __name__ == "__main__":
    main()
