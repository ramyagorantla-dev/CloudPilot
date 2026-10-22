
import streamlit as st
from rag_engine import build_report

# Configure the webpage
st.set_page_config(
    page_title="CloudPilot",
    page_icon="☁️",
    layout="centered"
)

# Page heading
st.title("☁️ CloudPilot")
st.subheader("Cloud Troubleshooting Assistant")
st.write(
    "Describe a cloud problem to find relevant troubleshooting "
    "guidance from the CloudPilot knowledge base."
)

# User input
question = st.text_area(
    "Describe your cloud issue:",
    placeholder="Example: My EC2 instance is unreachable...",
    height=100
)

# Search button
if st.button("Troubleshoot", type="primary"):
    if not question.strip():
        st.warning("Please describe your cloud issue first.")
    else:
        with st.spinner("Searching troubleshooting knowledge..."):
            report = build_report(question.strip())

        st.markdown("### Troubleshooting Report")
        st.write(report["message"])

        if report["sources"]:
            for source in report["sources"]:
                with st.container(border=True):
                    st.markdown(f"**Issue:** {source['issue']}")
                    st.write(f"**Service:** {source['service']}")
                    st.write(f"**Recommended checks:** {source['steps']}")
                    st.caption(
                        f"Source: {source['source_id']} "
                        f"| Similarity: {source['similarity']}"
                    )
        else:
            st.info(
                "No sufficiently similar guidance was found. "
                "Try including the service name or exact error."
            )

st.divider()
st.caption("CloudPilot | Local semantic search and evidence-based guidance")
