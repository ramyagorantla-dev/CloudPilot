import streamlit as st

from rag_engine import build_report


st.set_page_config(
    page_title="CloudPilot | AI Troubleshooting",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bright blue / purple / pink visual theme.
st.markdown(
    """
    <style>
    .stApp {
        background:
          radial-gradient(ellipse at 8% 0%, #dff4ff 0%, transparent 34%),
          radial-gradient(ellipse at 95% 10%, #f3e6ff 0%, transparent 35%),
          linear-gradient(135deg, #f8fbff 0%, #f5f3ff 55%, #fff5fb 100%);
    }
    .block-container {max-width: 1450px; padding-top: 1.5rem; padding-bottom: 2rem;}
    #MainMenu {visibility:hidden;} footer {visibility:hidden;}
    header[data-testid="stHeader"] {background:transparent;}
    section[data-testid="stSidebar"] {
        background:linear-gradient(180deg,#071b49 0%,#102d73 58%,#25175f 100%);
        border-right:1px solid rgba(255,255,255,.15);
    }
    section[data-testid="stSidebar"] * {color:#f7faff;}
    section[data-testid="stSidebar"] hr {border-color:rgba(255,255,255,.2);}
    .brand-title {
        font-size:clamp(2.7rem,6vw,4.8rem);font-weight:900;line-height:1.05;
        letter-spacing:-2px;margin:0;
        background:linear-gradient(90deg,#0875f5,#6545f5 52%,#e34cc9);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    }
    .hero-subtitle {color:#102b68;font-size:clamp(1.05rem,2.4vw,1.55rem);font-weight:800;margin:.6rem 0;}
    .hero-description {color:#52648a;font-size:1.02rem;line-height:1.75;}
    .hero-art {
        min-height:225px;display:flex;align-items:center;justify-content:center;text-align:center;
        border-radius:28px;background:linear-gradient(135deg,rgba(71,167,255,.2),rgba(155,110,255,.2),rgba(255,138,219,.22));
        border:1px solid rgba(120,145,255,.3);box-shadow:0 14px 40px rgba(83,100,200,.1);padding:1rem;
    }
    .hero-emoji {font-size:5rem;line-height:1.2;filter:drop-shadow(0 12px 12px rgba(50,80,180,.18));}
    .hero-art-title {color:#193d8c;font-size:1.1rem;font-weight:850;margin-top:.4rem;}
    .hero-art-caption {color:#60749d;font-size:.88rem;margin-top:.25rem;}
    .gradient-divider {height:4px;border-radius:100px;background:linear-gradient(90deg,#04b7ff,#5148ff,#b34dff,#ff68c8);margin:1.2rem 0 1.5rem;}
    .section-title {color:#112b68;font-size:1.4rem;font-weight:850;margin:.6rem 0 .5rem;}
    .section-caption {color:#6a7897;font-size:.92rem;margin-bottom:.9rem;}
    .platform-row {display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0;}
    .platform-pill {display:inline-flex;align-items:center;gap:.3rem;padding:.5rem .8rem;border-radius:999px;background:rgba(255,255,255,.85);border:1px solid #dbe5ff;color:#193d86;font-size:.87rem;font-weight:750;box-shadow:0 3px 12px rgba(80,100,170,.06);}
    div[data-testid="stTextArea"] textarea {border:1.5px solid #ccd8ff;border-radius:17px;background:rgba(255,255,255,.95);color:#172b57;font-size:1rem;padding:1rem;box-shadow:0 5px 18px rgba(73,90,170,.05);}
    div[data-testid="stTextArea"] textarea:focus {border-color:#7958ff;box-shadow:0 0 0 3px rgba(121,88,255,.13);}
    .stButton>button,.stFormSubmitButton>button {border:0!important;border-radius:14px!important;font-weight:800!important;min-height:46px;transition:transform .18s ease,box-shadow .18s ease;}
    .stFormSubmitButton>button {background:linear-gradient(100deg,#0875ff,#5948ff 55%,#bc43e8)!important;color:white!important;box-shadow:0 8px 22px rgba(90,75,240,.25);}
    .stButton>button:hover,.stFormSubmitButton>button:hover {transform:translateY(-2px);box-shadow:0 12px 28px rgba(90,75,240,.25);}
    .feature-card {height:100%;min-height:145px;padding:1.05rem;border-radius:20px;border:1px solid rgba(170,185,255,.45);background:rgba(255,255,255,.82);box-shadow:0 8px 25px rgba(56,75,155,.07);}
    .feature-icon {font-size:1.9rem;margin-bottom:.35rem;}
    .feature-title {color:#1b3477;font-weight:850;font-size:1rem;margin-bottom:.35rem;}
    .feature-text {color:#657492;font-size:.88rem;line-height:1.55;}
    .result-banner {padding:.9rem 1.1rem;border-radius:16px;background:linear-gradient(105deg,rgba(43,153,255,.12),rgba(126,86,255,.12),rgba(232,99,207,.1));border:1px solid #d8dfff;color:#16377e;font-weight:700;margin:.7rem 0 1rem;}
    .app-footer {text-align:center;color:#73809f;font-size:.84rem;padding:1.2rem 0 .5rem;}
    @media(max-width:700px){.block-container{padding-top:1rem}.brand-title{letter-spacing:-1px}.hero-art{min-height:160px}.hero-emoji{font-size:3.8rem}}
    </style>
    """,
    unsafe_allow_html=True,
)

CATEGORIES = [
    "All categories",
    "Cloud & Infrastructure",
    "Programming & Runtime",
    "DevOps & Infrastructure",
    "Databases & APIs",
    "AI & LLM Applications",
]

EXAMPLES = {
    "🟠 AWS: EC2 connection": ("Cloud & Infrastructure", "My AWS EC2 instance is unreachable."),
    "🔷 Azure: Remote Desktop": ("Cloud & Infrastructure", "My Azure virtual machine is not accepting Remote Desktop connections."),
    "🌈 Google Cloud: SSH": ("Cloud & Infrastructure", "My Google Cloud Compute Engine VM SSH connection fails."),
    "🔵 Kubernetes: CrashLoopBackOff": ("DevOps & Infrastructure", "My Kubernetes pod is stuck in CrashLoopBackOff."),
    "🐍 Python: missing package": ("Programming & Runtime", "My Python application raises ModuleNotFoundError for a package."),
    "🐳 Docker: container exits": ("DevOps & Infrastructure", "My Docker container exits immediately after starting."),
    "🗄️ SQL: unexpected results": ("Databases & APIs", "My SQL query returns unexpected duplicate rows."),
    "🤖 RAG: irrelevant retrieval": ("AI & LLM Applications", "My RAG application retrieves irrelevant documents for a question."),
    "🧪 Unrelated question": ("All categories", "What is the best restaurant in New York?"),
}

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0 1.1rem;">
          <div style="font-size:4rem;">☁️</div>
          <div style="font-size:2rem;font-weight:900;letter-spacing:-1px;">CloudPilot</div>
          <div style="color:#c4d9ff;font-size:.92rem;margin-top:.4rem;">Your AI Troubleshooting Copilot</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.radio(
        "Navigate",
        ["🏠 Home", "💡 Examples", "⚙️ How It Works", "🌍 Supported Categories"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("### 🧰 Technology coverage")
    st.markdown("""
    **☁️ Cloud**  
    AWS · Azure · Google Cloud

    **🐍 Programming**  
    Python · Java · JavaScript

    **🛠️ DevOps**  
    Kubernetes · Docker · Linux · Git · CI/CD

    **🗄️ Databases & APIs**  
    SQL · MySQL · REST APIs

    **🤖 AI & LLMs**  
    RAG · Embeddings · LLM APIs
    """)
    st.divider()
    st.markdown("<div style='text-align:center;padding:.7rem 0;color:#d9e7ff;line-height:1.7'><div style='font-size:2rem'>🚀</div><b>Less downtime.<br/>More building.</b></div>", unsafe_allow_html=True)

hero_left, hero_right = st.columns([1.55, 1], gap="large")
with hero_left:
    st.markdown('<p class="brand-title">CloudPilot ✦</p>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Your AI Assistant for Troubleshooting</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-description">
      From cloud infrastructure to Python errors and AI application issues,
      describe the problem and get a troubleshooting plan grounded in relevant
      knowledge-base evidence.
    </div>
    <div class="platform-row">
      <span class="platform-pill">☁️ Cloud</span>
      <span class="platform-pill">🐍 Programming</span>
      <span class="platform-pill">🛠️ DevOps</span>
      <span class="platform-pill">🗄️ Databases & APIs</span>
      <span class="platform-pill">🤖 AI & LLMs</span>
    </div>
    """, unsafe_allow_html=True)
with hero_right:
    st.markdown("""
    <div class="hero-art"><div>
      <div class="hero-emoji">🤖☁️</div>
      <div class="hero-art-title">Meet your troubleshooting copilot</div>
      <div class="hero-art-caption">Search smarter. Solve problems faster.</div>
      <div style="font-size:1.5rem;margin-top:.6rem">🐍 🐳 ☁️ 🤖</div>
    </div></div>
    """, unsafe_allow_html=True)
st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

if page == "⚙️ How It Works":
    st.markdown('<div class="section-title">✨ How CloudPilot works</div>', unsafe_allow_html=True)
    st.write("CloudPilot retrieves relevant troubleshooting knowledge and uses Gemini to generate an evidence-grounded response.")
    stages = [
        ("1️⃣", "Describe", "Enter a question, technology, and error message."),
        ("2️⃣", "Retrieve", "Semantic search finds related knowledge-base entries."),
        ("3️⃣", "Filter", "A relevance threshold filters weaker matches."),
        ("4️⃣", "Generate", "Gemini creates a beginner-friendly troubleshooting plan."),
        ("5️⃣", "Verify", "Review sources before changing a real system."),
    ]
    cols = st.columns(len(stages))
    for col, (icon, title, description) in zip(cols, stages):
        with col:
            st.markdown(f'<div class="feature-card"><div class="feature-icon">{icon}</div><div class="feature-title">{title}</div><div class="feature-text">{description}</div></div>', unsafe_allow_html=True)
    st.info("CloudPilot provides guidance; it does not directly inspect or modify your systems.")

elif page == "🌍 Supported Categories":
    st.markdown('<div class="section-title">🌍 Explore CloudPilot categories</div>', unsafe_allow_html=True)
    categories = [
        ("☁️", "Cloud & Infrastructure", "AWS, Microsoft Azure, Google Cloud", "VM connectivity, storage permissions, and monitoring."),
        ("🐍", "Programming & Runtime", "Python, Java, JavaScript", "Exceptions, imports, environment configuration, and runtime issues."),
        ("🛠️", "DevOps & Infrastructure", "Kubernetes, Docker, Linux, Git, CI/CD", "Container failures, deployments, pipelines, and services."),
        ("🗄️", "Databases & APIs", "SQL, MySQL, REST APIs", "Query issues, connection failures, authentication, and rate limits."),
        ("🤖", "AI & LLM Applications", "LLM APIs, RAG, embeddings", "Quota errors, poor retrieval, embedding similarity, and grounding."),
    ]
    for i in range(0, len(categories), 2):
        cols = st.columns(2)
        for col, (emoji, title, tech, desc) in zip(cols, categories[i:i + 2]):
            with col:
                st.markdown(f'<div class="feature-card"><div class="feature-icon">{emoji}</div><div class="feature-title">{title}</div><div style="color:#455f97;font-weight:700">{tech}</div><div class="feature-text" style="margin-top:.6rem">{desc}</div></div>', unsafe_allow_html=True)
                st.write("")
    st.caption("Coverage is limited to the starter knowledge-base topics included with this project. Add and evaluate more entries as you expand it.")

elif page == "💡 Examples":
    st.markdown('<div class="section-title">💡 Try a sample troubleshooting question</div>', unsafe_allow_html=True)
    for title, (_, example) in EXAMPLES.items():
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.code(example, language=None)
    st.info("Choose Home in the sidebar, select a sample from the dropdown, and submit it.")

else:
    st.markdown('<div class="section-title">💡 Start with an example</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Select a sample issue or describe your own.</div>', unsafe_allow_html=True)
    selected_example = st.selectbox("Sample question", ["Choose an example..."] + list(EXAMPLES.keys()))
    default_category, default_question = EXAMPLES.get(selected_example, ("All categories", ""))

    with st.form("cloudpilot_troubleshooting_form"):
        category = st.selectbox("Technology category", CATEGORIES, index=CATEGORIES.index(default_category))
        question = st.text_area(
            "Describe your issue",
            value=default_question,
            placeholder="Example: My Python application raises ModuleNotFoundError when I run it...",
            height=125,
            max_chars=2000,
            help="Include the technology, service, and exact error message when possible.",
        )
        submitted = st.form_submit_button("🔍  Troubleshoot My Issue  →", type="primary", use_container_width=True)

    st.caption("✨ Semantic search • RAG • Gemini • Multi-technology troubleshooting")

    if submitted:
        cleaned_question = question.strip()
        if not cleaned_question:
            st.warning("Please describe your issue first.")
        else:
            try:
                with st.spinner("☁️ Searching knowledge and preparing your report..."):
                    report = build_report(cleaned_question, category=category)

                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📋 Your Troubleshooting Report</div>', unsafe_allow_html=True)
                if report.get("message"):
                    st.markdown(f'<div class="result-banner">{report["message"]}</div>', unsafe_allow_html=True)

                if report.get("answer"):
                    st.markdown("### 🤖 CloudPilot AI guidance")
                    st.markdown(report["answer"])

                sources = report.get("sources") or []
                if sources:
                    st.markdown("### 📚 Evidence behind this answer")
                    st.caption("These are the knowledge-base entries retrieved for your question.")
                    for number, source in enumerate(sources, start=1):
                        with st.container(border=True):
                            st.markdown(f"#### {number}. {source.get('issue', 'Troubleshooting entry')}")
                            col1, col2, col3 = st.columns(3)
                            col1.caption("CATEGORY")
                            col1.write(source.get("category", "Other"))
                            col2.caption("PROVIDER / TECHNOLOGY")
                            col2.write(source.get("provider", "Not specified"))
                            col3.caption("SERVICE")
                            col3.write(source.get("service", "Not specified"))
                            if source.get("steps"):
                                st.markdown("**Recommended checks**")
                                st.write(source["steps"])
                            adjusted = source.get("adjusted_score")
                            semantic = source.get("similarity")
                            if adjusted is not None:
                                st.progress(max(0.0, min(1.0, float(adjusted))), text=f"Retrieval relevance score: {float(adjusted):.3f}")
                            if semantic is not None:
                                st.caption(f"Semantic similarity: {float(semantic):.3f}")
                            if source.get("source_url"):
                                st.link_button("📖 Open documentation", source["source_url"])
                            if source.get("source_id"):
                                st.caption(f"Knowledge-base ID: {source['source_id']}")
                elif not report.get("answer"):
                    st.info("No sufficiently relevant evidence was found. Try a more specific question or select All categories.")

                st.caption("Retrieval scores are ranking signals, not calibrated confidence. Verify recommendations before making production changes.")
            except Exception as exc:
                st.error("CloudPilot could not complete this request. Please try again.")
                st.caption(f"Technical error type: {type(exc).__name__}. Check terminal or deployment logs; do not share API keys.")

if page == "🏠 Home":
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✨ Why choose CloudPilot?</div>', unsafe_allow_html=True)
    features = [
        ("⚡", "Semantic Search", "Find related guidance beyond exact keyword matches."),
        ("🧠", "RAG-Powered", "Generate answers using retrieved evidence as context."),
        ("📚", "Source-Aware", "Review knowledge entries and configured documentation links."),
        ("🌍", "Multi-Technology", "Starter coverage for cloud, code, DevOps, data, and AI."),
    ]
    cols = st.columns(4)
    for col, (emoji, title, desc) in zip(cols, features):
        with col:
            st.markdown(f'<div class="feature-card"><div class="feature-icon">{emoji}</div><div class="feature-title">{title}</div><div class="feature-text">{desc}</div></div>', unsafe_allow_html=True)

st.markdown("""
<div class="app-footer">
  <b style="color:#334b91;">☁️ CloudPilot</b> &nbsp; | &nbsp;
  Semantic Search • RAG • Gemini • Multi-Technology<br/><br/>
  Portfolio prototype. Verify recommendations before applying changes to real systems.
</div>
""", unsafe_allow_html=True)
