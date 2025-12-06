import streamlit as st
import pandas as pd

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="SGPA & CGPA Calculator",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 SGPA & CGPA Calculator")
st.caption("Accurate CGPA using Σ(Credit × GradePoint) / Σ(Credits) across all semesters.")

# ---------- GRADE SCHEMES ----------
GRADE_SCHEMES = {
    "10-point (O, A+/E, A, B, C, D, D', F, I)": {
        "O": 10,
        "A+/E": 9,
        "A": 8,
        "B": 7,
        "C": 6,
        "D": 5,
        "D'": 4,
        "F": 2,
        "I": 0,
    }
}

# ---------- SIDEBAR SETTINGS ----------
st.sidebar.header("Settings ⚙️")

scheme_name = st.sidebar.selectbox(
    "Select Grade Scheme",
    list(GRADE_SCHEMES.keys())
)
grade_points_map = GRADE_SCHEMES[scheme_name]

st.sidebar.markdown("**Current Grade Scale:**")
for grade, points in grade_points_map.items():
    st.sidebar.write(f"- {grade}: {points} points")

# Initialize session state for storing semester totals
if "records" not in st.session_state:
    st.session_state["records"] = []    # {"semester": n, "credits": x, "points": y}

# ---------- TABS ----------
sgpa_tab, cgpa_tab = st.tabs(["📘 SGPA Calculator", "📚 CGPA Calculator"])

# -------------------------------------------------------------------
# ------------------------ SGPA TAB ---------------------------------
# -------------------------------------------------------------------
with sgpa_tab:
    st.subheader("📘 Semester SGPA Calculator")

    col1, col2 = st.columns(2)
    with col1:
        semester = st.number_input("Semester Number", 1, 12, 1)
    with col2:
        num_subjects = st.number_input("Number of Subjects", 1, 20, 5)

    st.markdown("### 📝 Enter Subject Details")

    subjects_data = []

    for i in range(int(num_subjects)):
        c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1.5])

        with c1:
            name = st.text_input(f"Subject {i+1}", key=f"name_{semester}_{i}")
        with c2:
            credit = st.number_input(f"Credits {i+1}", 0.0, 10.0, 3.0, key=f"credit_{semester}_{i}")
        with c3:
            grade = st.selectbox(f"Grade {i+1}", list(grade_points_map.keys()), key=f"grade_{semester}_{i}")
        with c4:
            gp = grade_points_map[grade]
            st.write(f"GP: **{gp}**")

        subjects_data.append({
            "name": name,
            "credit": credit,
            "grade": grade,
            "gp": gp,
            "total_points": credit * gp,
        })

    if st.button("✅ Calculate SGPA", type="primary"):
        df = pd.DataFrame(subjects_data)

        total_credits = df["credit"].sum()
        total_points = df["total_points"].sum()

        if total_credits == 0:
            st.error("Credits cannot be zero.")
        else:
            sgpa = total_points / total_credits

            st.success(f"🎉 SGPA for Semester {semester} = **{sgpa:.2f}**")
            st.metric(f"SGPA (Sem {semester})", f"{sgpa:.2f}")

            # -------- REMOVE OLD ENTRY IF SAME SEMESTER -------
            st.session_state["records"] = [
                r for r in st.session_state["records"] if r["semester"] != semester
            ]

            # -------- ADD NEW SEMESTER DATA -------------------
            st.session_state["records"].append({
                "semester": semester,
                "credits": float(total_credits),
                "points": float(total_points)
            })

            # -------- ALWAYS SORT BY SEMESTER ------------------
            st.session_state["records"] = sorted(
                st.session_state["records"], key=lambda x: x["semester"]
            )

            with st.expander("📊 Detailed Table"):
                st.dataframe(df)

            st.info("Semester saved. You may now go to the CGPA Calculator tab.")


# -------------------------------------------------------------------
# ------------------------ CGPA TAB ---------------------------------
# -------------------------------------------------------------------
with cgpa_tab:
    st.subheader("📚 CGPA Calculator")

    if len(st.session_state["records"]) == 0:
        st.warning("No SGPA data yet. First calculate SGPA for at least one semester.")
    else:
        st.markdown("### 📄 Semester Summary")

        df = pd.DataFrame(st.session_state["records"])
        df = df.sort_values("semester")

        df_display = df.rename(columns={
            "semester": "Semester",
            "credits": "Total Credits",
            "points": "Σ(C × GP)"
        })

        df_display["SGPA"] = df_display["Σ(C × GP)"] / df_display["Total Credits"]

        st.dataframe(df_display, use_container_width=True)

        total_credits_all = df["credits"].sum()
        total_points_all = df["points"].sum()

        if total_credits_all == 0:
            st.error("Cannot compute CGPA because total credits = 0.")
        else:
            cgpa = total_points_all / total_credits_all

            st.markdown("---")
            st.metric(
                label="🎓 Final CGPA (Exact Formula)",
                value=f"{cgpa:.2f}",
                help="CGPA = Σ(Credit × GradePoint) / Σ(Credits) across ALL semesters."
            )

            st.caption(
                f"Based on {len(df)} semesters and total **{total_credits_all:.0f} credits**."
            )

        st.markdown("---")
        if st.button("🗑 Clear All Semesters", type="secondary"):
            st.session_state["records"] = []
            st.success("All data cleared.")
