import streamlit as st
import os
import tempfile
import plotly.graph_objects as go
from text_extractor import extract_text
from keyword_scanner import scan_resume_vs_jd
from bert_scorer import bert_similarity_score, hybrid_score
from ats_checker import check_ats
from recommender import get_recommendations

st.set_page_config(
    page_title="Resume Keyword Scanner — Resume Analyzer",
    page_icon="",
    layout="wide"
)

# ── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 5px 0;
    }
    .keyword-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.85rem;
    }
    .course-card {
        background: #f0f7ff;
        border: 1px solid #cce0ff;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────
st.markdown('<p class="main-title">📄 Resume Keyword Scanner</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI-Powered Resume & Job Description Analyzer</p>', unsafe_allow_html=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# ── File Upload ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📋 Upload Resume")
    resume_file = st.file_uploader(
        "PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        key="resume"
    )
    if resume_file:
        if resume_file.size > MAX_FILE_SIZE:
            st.error("File too large (max 5MB)")
            resume_file = None
        else:
            st.success(f"✅ {resume_file.name} ({resume_file.size/1024:.1f} KB)")

with col2:
    st.markdown("#### 🎯 Upload Job Description")
    jd_file = st.file_uploader(
        "PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        key="jd"
    )
    if jd_file:
        if jd_file.size > MAX_FILE_SIZE:
            st.error("File too large (max 5MB)")
            jd_file = None
        else:
            st.success(f"✅ {jd_file.name} ({jd_file.size/1024:.1f} KB)")

st.divider()

# ── Analyse Button ───────────────────────────────────────────
if st.button("🔍 Analyse Resume", use_container_width=True, type="primary"):
    if not resume_file or not jd_file:
        st.warning("⚠️ Please upload both Resume and Job Description")
    else:
        with st.spinner("Extracting text..."):
            try:
                # Save temp files
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix="." + resume_file.name.split(".")[-1]
                ) as f:
                    f.write(resume_file.getbuffer())
                    resume_path = f.name

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix="." + jd_file.name.split(".")[-1]
                ) as f:
                    f.write(jd_file.getbuffer())
                    jd_path = f.name

                resume_text = extract_text(resume_path)
                jd_text     = extract_text(jd_path)

                os.remove(resume_path)
                os.remove(jd_path)

                if not resume_text.strip():
                    st.error("❌ Could not extract text from Resume")
                    st.stop()
                if not jd_text.strip():
                    st.error("❌ Could not extract text from Job Description")
                    st.stop()

            except Exception as e:
                st.error(f"❌ Extraction error: {str(e)}")
                st.stop()

        with st.spinner("Running AI analysis... (first run takes ~20 seconds for BERT model)"):
            # TF-IDF scan
            tfidf_score, common, missing, tech_missing, other_missing = scan_resume_vs_jd(
                resume_text, jd_text
            )

            # BERT semantic score
            bert_result = bert_similarity_score(resume_text, jd_text)
            bert_sc     = bert_result["bert_score"]

            # Hybrid final score
            final_score = hybrid_score(tfidf_score, bert_sc)

            # ATS check
            ats_result = check_ats(resume_text)

            # Course recommendations
            courses = get_recommendations(missing)

        st.success("✅ Analysis Complete!")
        st.divider()

        # ── SCORES ROW ───────────────────────────────────────
        st.markdown("### 📊 Score Overview")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                label="🎯 Final Score",
                value=f"{final_score}%",
                help="40% TF-IDF + 60% BERT semantic score"
            )
        with c2:
            st.metric(
                label="🔤 Keyword Match",
                value=f"{tfidf_score}%",
                help="Exact keyword overlap (TF-IDF)"
            )
        with c3:
            st.metric(
                label="🧠 Semantic Match",
                value=f"{bert_sc}%",
                help="Meaning-based similarity (BERT)"
            )
        with c4:
            st.metric(
                label="🤖 ATS Score",
                value=f"{ats_result['ats_score']}%",
                help="ATS compatibility score"
            )

        st.divider()

        # ── GAUGE CHARTS ─────────────────────────────────────
        g1, g2 = st.columns(2)

        def make_gauge(value, title, color):
            fig = go.Figure(go.Indicator(
                mode  = "gauge+number",
                value = value,
                title = {"text": title, "font": {"size": 14}},
                gauge = {
                    "axis": {"range": [0, 100]},
                    "bar":  {"color": color},
                    "steps": [
                        {"range": [0,  50], "color": "#ffe0e0"},
                        {"range": [50, 75], "color": "#fff3cd"},
                        {"range": [75, 100],"color": "#d4edda"},
                    ],
                    "threshold": {
                        "line":  {"color": "black", "width": 3},
                        "thickness": 0.75,
                        "value": value
                    }
                }
            ))
            fig.update_layout(height=250, margin=dict(t=40, b=10, l=20, r=20))
            return fig

        with g1:
            st.plotly_chart(
                make_gauge(final_score, "Final Hybrid Score", "#1f77b4"),
                use_container_width=True
            )
        with g2:
            st.plotly_chart(
                make_gauge(ats_result["ats_score"], "ATS Compatibility", "#2ca02c"),
                use_container_width=True
            )

        st.divider()

        # ── TABS ─────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔑 Keywords",
            "🤖 ATS Report",
            "📚 Courses",
            "💡 Tips"
        ])

        # TAB 1 — Keywords
        with tab1:
            k1, k2 = st.columns(2)

            with k1:
                st.markdown("#### ✅ Keywords You Have")
                st.caption(f"{len(common)} keywords matched")
                if common:
                    badges = " ".join([
                        f'<span style="background:#d4edda;color:#155724;'
                        f'padding:3px 10px;border-radius:20px;'
                        f'margin:3px;display:inline-block;font-size:0.85rem">'
                        f'{k}</span>'
                        for k in sorted(common)
                    ])
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.info("No matching keywords found")

            with k2:
                st.markdown("#### ❌ Keywords to Add")
                st.caption(f"{len(missing)} keywords missing")
                if tech_missing:
                    st.error("🔴 Critical Technical Skills:")
                    badges = " ".join([
                        f'<span style="background:#f8d7da;color:#721c24;'
                        f'padding:3px 10px;border-radius:20px;'
                        f'margin:3px;display:inline-block;font-size:0.85rem">'
                        f'{k}</span>'
                        for k in sorted(tech_missing)
                    ])
                    st.markdown(badges, unsafe_allow_html=True)

                if other_missing:
                    st.warning("🟡 Recommended to Add:")
                    badges = " ".join([
                        f'<span style="background:#fff3cd;color:#856404;'
                        f'padding:3px 10px;border-radius:20px;'
                        f'margin:3px;display:inline-block;font-size:0.85rem">'
                        f'{k}</span>'
                        for k in sorted(other_missing)
                    ])
                    st.markdown(badges, unsafe_allow_html=True)

            # Bar chart
            st.divider()
            st.markdown("#### 📊 Keyword Breakdown")
            fig = go.Figure(go.Bar(
                x=["Matched", "Missing"],
                y=[len(common), len(missing)],
                marker_color=["#28a745", "#dc3545"],
                text=[len(common), len(missing)],
                textposition="auto"
            ))
            fig.update_layout(
                height=300,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        # TAB 2 — ATS Report
        with tab2:
            st.markdown("#### 🤖 ATS Compatibility Report")
            st.caption("Checks if your resume is readable by Applicant Tracking Systems")

            # Sections found
            st.markdown("**Resume Sections Detected:**")
            sec_cols = st.columns(4)
            for i, (section, found) in enumerate(ats_result["sections_found"].items()):
                with sec_cols[i % 4]:
                    if found:
                        st.success(f"✅ {section.title()}")
                    else:
                        st.error(f"❌ {section.title()}")

            st.divider()

            # Issues
            if ats_result["issues"]:
                st.markdown("**Issues Found:**")
                for issue in ats_result["issues"]:
                    st.error(f"⚠️ {issue}")
            else:
                st.success("✅ No major ATS issues found!")

            # Tips
            if ats_result["tips"]:
                st.markdown("**Recommendations:**")
                for tip in ats_result["tips"]:
                    st.info(f"💡 {tip}")

            st.caption(f"Resume word count: {ats_result['word_count']} words")

        # TAB 3 — Courses
        with tab3:
            st.markdown("#### 📚 Recommended Courses for Missing Skills")

            if courses:
                st.caption(f"Based on {len(missing)} missing keywords, here are courses to bridge your skill gap:")
                for course in courses:
                    st.markdown(f"""
<div style="background:#f0f7ff;border:1px solid #cce0ff;
border-radius:10px;padding:12px 16px;margin:8px 0">
<strong style="color:#1a1a2e">{course['title']}</strong><br>
<span style="color:#444;font-size:0.85rem">
For skill: <code>{course['for_skill']}</code> &nbsp;|&nbsp;
Platform: <strong>{course['platform']}</strong>
</span><br>
<a href="{course['url']}" target="_blank"
style="color:#1f77b4;font-size:0.85rem">
🔗 View Course →</a>
</div>
""", unsafe_allow_html=True)
            else:
                st.success("🎉 No course recommendations needed — great skill match!")

        # TAB 4 — Tips
        with tab4:
            st.markdown("#### 💡 Personalised Improvement Tips")

            if final_score >= 75:
                st.success("🌟 Excellent match! Your resume aligns very well with this job.")
            elif final_score >= 50:
                st.warning("📈 Good match! A few improvements will significantly boost your chances.")
            else:
                st.error("⚠️ Low match. Focus on adding the critical missing keywords.")

            st.markdown("**Action Items:**")

            if tech_missing:
                st.markdown(
                    f"1. 🎯 Add these **{len(tech_missing)} critical technical skills** "
                    f"to your resume: `{'`, `'.join(sorted(tech_missing)[:5])}`"
                )
            if other_missing:
                st.markdown(
                    f"2. 📝 Include these **{len(other_missing)} additional keywords** "
                    f"where relevant: `{'`, `'.join(sorted(other_missing)[:5])}`"
                )
            if ats_result["issues"]:
                st.markdown(
                    f"3. 🤖 Fix **{len(ats_result['issues'])} ATS issues** "
                    f"found in the ATS Report tab"
                )
            if bert_sc < tfidf_score:
                st.markdown(
                    "4. 🧠 Your resume has the right keywords but the **overall meaning "
                    "doesn't align well** — rewrite experience bullets to better reflect "
                    "the job requirements"
                )
            if bert_sc > tfidf_score:
                st.markdown(
                    "4. 🔤 Your resume **semantically aligns well** but lacks exact "
                    "keyword matches — add the specific terms from the job description"
                )

            st.divider()
            st.markdown("**Score Explanation:**")
            st.markdown(f"""
| Score | Value | Meaning |
|-------|-------|---------|
| Final Score | {final_score}% | Weighted average of TF-IDF + BERT |
| Keyword Match | {tfidf_score}% | Exact keyword overlap |
| Semantic Match | {bert_sc}% | Meaning-based similarity (BERT) |
| ATS Score | {ats_result['ats_score']}% | Resume formatting compatibility |
""")
