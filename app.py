import streamlit as st
import pandas as pd
import json, os, uuid
from google.cloud import firestore_v1

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="SGPA & CGPA Calculator",
    page_icon="🎓",
    layout="wide",
)

# ---------- FIRESTORE INITIALIZATION ----------
# Convert SecretValue objects → normal Python dict
key_dict = {key: str(st.secrets["GOOGLE"][key]) for key in st.secrets["GOOGLE"]}

# Write temporary service-account JSON
with open("gcp_key.json", "w") as f:
    json.dump(key_dict, f)

# Point Google client to credentials file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_key.json"

# Firestore Client
db = firestore_v1.Client()


# ---------- VISITOR COUNTER ----------
visitors_ref = db.collection("metrics").document("visitors")

# Count only once per Streamlit session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

    try:
        transaction = db.transaction()

        @firestore_v1.transactional
        def increment_visitors(transaction, doc_ref):
            snapshot = doc_ref.get(transaction=transaction)
            current = snapshot.get("count") if snapshot.exists else 0
            transaction.set(doc_ref, {"count": current + 1})

        increment_visitors(transaction, visitors_ref)

    except Exception as e:
        st.sidebar.error(f"❌ Firestore Error: {e}")

# Read visitor count
try:
    doc = visitors_ref.get()
    visitor_count = doc.to_dict().get("count", 0) if doc.exists else 0
except:
    visitor_count = 0


# ---------- CUSTOM BUTTON CSS ----------
st.markdown("""
    <style>
        .calc-sgpa button {
            background-color: #8A2BE2 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.2rem;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)


# ---------- HEADER ----------
st.title("🎓 SGPA & CGPA Calculator")
st.caption("Accurate CGPA using Σ(Credit × GradePoint) / Σ(Credits) across all semesters.")


# ---------- GRADE SCHEME ----------
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


# ---------- SIDEBAR ----------
st.sidebar.header("Settings ⚙️")
st.sidebar.markdown(f"👥 **Total Visitors:** {visitor_count}")

scheme_name = st.sidebar.selectbox("Select Grade Scheme", list(GRADE_SCHEMES.keys()))
grade_points_map = GRADE_SCHEMES[scheme_name]

st.sidebar.markdown("**Current Grade Scale:**")
for grade, pts in grade_points_map.items():
    st.sidebar.write(f"- {grade}: {pts} points")


# Initialize stored SGPA records
if "records" not in st.session_state:
    st.session_state["records"] = []


# ---------- TABS ----------
sgpa_tab, cgpa_tab = st.tabs(["📘 SGPA Calculator", "📚 CGPA Calculator"])


# ---------- SGPA TAB ----------
with sgpa_tab:
    st.subheader("📘 Semester SGPA Calculator")

    col1, col2 = st.columns(2)
    semester = col1.number_input("Semester Number", 1, 12, 1)
    num_subjects = col2.number_input("Number of Subjects", 1, 20, 5)

    st.markdown("### 📝 Enter Subject Details")

    subjects_data = []
    for i in range(int(num_subjects)):
        c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1.5])

        name = c1.text_input(f"Subject {i+1}", key=f"name_{semester}_{i}")
        credit = c2.number_input(f"Credits {i+1}", 0.0, 10.0, 3.0, key=f"credit_{semester}_{i}")
        grade = c3.selectbox(f"Grade {i+1}", list(grade_points_map.keys()), key=f"grade_{semester}_{i}")
        gp = grade_points_map[grade]
        c4.write(f"GP: **{gp}**")

        subjects_data.append({
            "name": name,
            "credit": credit,
            "grade": grade,
            "gp": gp,
            "total_points": credit * gp
        })

    st.markdown('<div class="calc-sgpa">', unsafe_allow_html=True)
    clicked = st.button("Calculate SGPA")
    st.markdown("</div>", unsafe_allow_html=True)

    if clicked:
        df = pd.DataFrame(subjects_data)
        total_credits = df["credit"].sum()
        total_points = df["total_points"].sum()

        if total_credits == 0:
            st.error("Credits cannot be zero.")
        else:
            sgpa = total_points / total_credits
            st.success(f"🎉 SGPA for Semester {semester} = **{sgpa:.2f}**")

            st.metric(f"SGPA (Sem {semester})", f"{sgpa:.2f}")

            # Remove previous entry if same semester
            st.session_state["records"] = [
                r for r in st.session_state["records"]
                if r["semester"] != semester
            ]

            st.session_state["records"].append({
                "semester": semester,
                "credits": float(total_credits),
                "points": float(total_points)
            })


# ---------- CGPA TAB ----------
with cgpa_tab:
    st.subheader("📚 CGPA Calculator")

    if len(st.session_state["records"]) == 0:
        st.warning("No SGPA data yet. Calculate SGPA first.")
    else:
        df = pd.DataFrame(st.session_state["records"]).sort_values("semester")

        df_display = df.rename(columns={
            "semester": "Semester",
            "credits": "Total Credits",
            "points": "Σ(C × GP)"
        })
        df_display["SGPA"] = df_display["Σ(C × GP)"] / df_display["Total Credits"]

        st.dataframe(df_display, use_container_width=True)

        total_credits = df["credits"].sum()
        total_points = df["points"].sum()

        cgpa = total_points / total_credits if total_credits else 0

        st.metric("🎓 Final CGPA", f"{cgpa:.2f}")
        st.caption(f"Based on {len(df)} semesters and {total_credits:.0f} credits.")

        if st.button("🗑 Clear All Semesters", type="secondary"):
            st.session_state["records"] = []
            st.success("All data cleared.")
            st.rerun()
