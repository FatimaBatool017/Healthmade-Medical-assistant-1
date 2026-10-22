import datetime as dt

import pandas as pd
import streamlit as st

st.set_page_config(page_title="HealthMate", page_icon="💙", layout="centered")

DISCLAIMER = (
    "HealthMate gives general health information only. It does not replace a doctor "
    "and cannot diagnose conditions or prescribe medicine."
)

st.markdown(
    """
    <style>
    .stApp { background: #ffffff; }
    [data-testid="stSidebar"] { background: #EAF6FD; }
    h1, h2, h3 { color: #14506E; }
    .card { background:#EAF6FD; padding:14px 16px; border-radius:14px; margin-bottom:10px; }
    .warn { background:#FFEBEE; padding:14px 16px; border-radius:14px; margin-bottom:10px; }
    div.stButton > button { background:#3AA6E0; color:white; border:0; border-radius:10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Data lives only in this browser session (private to each visitor, cleared on refresh).
st.session_state.setdefault("meds", [])
st.session_state.setdefault("history", [])

SYMPTOMS = {
    "headache": ("Tension, dehydration, lack of sleep, eye strain, stress, migraine.",
                 "Rest, drink water, reduce screen time. See a doctor if it is sudden and severe, or keeps returning."),
    "fever": ("Common infections such as flu or cold, stomach infections, other illnesses.",
              "Rest and drink fluids. See a doctor if it lasts more than 3 days, is very high, or comes with a stiff neck or rash."),
    "cough": ("Cold, flu, allergies, throat irritation, asthma, smoking.",
              "Warm fluids and rest. See a doctor if it lasts over 2-3 weeks, or you cough blood or struggle to breathe."),
    "sore throat": ("Viral infections, strep throat, dry air, allergies.",
                    "Warm drinks, rest your voice. See a doctor if it lasts over a week or swallowing is very hard."),
    "stomach pain": ("Indigestion, gas, food poisoning, constipation, stomach infection.",
                     "Small light meals and fluids. Seek care if pain is severe, constant, or comes with vomiting blood or high fever."),
    "fatigue": ("Poor sleep, stress, low iron, thyroid issues, infections, low activity.",
                "Review sleep and diet. See a doctor if tiredness lasts for weeks without a clear reason."),
    "nausea": ("Stomach bug, food poisoning, motion sickness, migraine, pregnancy.",
               "Sip fluids slowly, eat bland food. Seek care if you cannot keep fluids down for a day."),
}

TIPS = [
    ("🥗 Healthy eating", "Fill half your plate with vegetables and fruit, choose whole grains, and limit sugary drinks and fried food."),
    ("🏃 Exercise", "Aim for about 30 minutes of movement most days, such as brisk walking. Start slowly and build up."),
    ("😴 Sleep", "Most adults need 7-9 hours. Keep regular sleep times and avoid screens before bed."),
    ("🧼 Hygiene", "Wash hands with soap for 20 seconds before eating and after using the toilet. Brush teeth twice a day."),
    ("💧 Hydration", "Drink water regularly through the day, especially in hot weather."),
]

DOCTORS = [
    ("Dr. Sample Khan", "General Physician", "City Care Clinic", "Mon-Sat, 9am-5pm"),
    ("Dr. Sample Ali", "Pediatrician", "Family Health Center", "Mon-Fri, 10am-4pm"),
    ("Dr. Sample Ahmed", "Dentist", "Smile Dental Clinic", "Tue-Sun, 11am-7pm"),
    ("Dr. Sample Noor", "Gynecologist", "Women's Care Hospital", "Mon-Sat, 9am-2pm"),
]

SIGNS = [
    "Chest pain or pressure",
    "Difficulty breathing",
    "Sudden weakness, face drooping, or slurred speech",
    "Severe bleeding that will not stop",
    "Fainting or loss of consciousness",
    "Seizure",
    "Sudden severe headache or confusion",
    "Severe allergic reaction (swelling of face or throat)",
    "Thoughts of harming yourself",
]

PAGES = ["🏠 Home", "🔍 Symptom Checker", "❤️ Health Tips", "💊 Medicine Reminder",
         "🏥 Doctors & Clinics", "📋 Health History", "🚨 Emergency Help"]
page = st.sidebar.radio("HealthMate", PAGES)
st.sidebar.caption(DISCLAIMER)

if page == PAGES[0]:
    st.title("Welcome to HealthMate 💙")
    st.write("Learn about common health problems and look after yourself, one day at a time. "
             "Use the menu on the left to get started.")
    c1, c2 = st.columns(2)
    c1.markdown('<div class="card">🔍 <b>Symptom Checker</b><br>General info on common symptoms</div>', unsafe_allow_html=True)
    c2.markdown('<div class="card">💊 <b>Medicine Reminder</b><br>Keep track of your medicines</div>', unsafe_allow_html=True)
    c1.markdown('<div class="card">❤️ <b>Health Tips</b><br>Eating, exercise, sleep, hygiene</div>', unsafe_allow_html=True)
    c2.markdown('<div class="warn">🚨 <b>Emergency Help</b><br>Know the warning signs</div>', unsafe_allow_html=True)
    st.info(DISCLAIMER)

elif page == PAGES[1]:
    st.title("Symptom Checker")
    picked = st.multiselect("Choose your symptoms", list(SYMPTOMS))
    text = st.text_input("Or describe them (e.g. fever and cough)")
    found = sorted(set(picked) | {s for s in SYMPTOMS if s in text.lower()})
    if st.button("Show general information"):
        if not found:
            st.write("No match in our small guide. If you are worried, please talk to a doctor or pharmacist.")
        for s in found:
            causes, care = SYMPTOMS[s]
            st.markdown(f'<div class="card"><h4>{s.title()}</h4><b>Common causes:</b> {causes}<br><br>'
                        f'<b>General advice:</b> {care}</div>', unsafe_allow_html=True)
    note = ", ".join(found) if found else text.strip()
    if st.button("Save to Health History") and note:
        st.session_state.history.insert(0, {"Date": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "Symptoms": note})
        st.success("Saved.")
    st.info(DISCLAIMER)

elif page == PAGES[2]:
    st.title("Health Tips")
    for title, body in TIPS:
        st.markdown(f'<div class="card"><b>{title}</b><br>{body}</div>', unsafe_allow_html=True)

elif page == PAGES[3]:
    st.title("Medicine Reminder")
    with st.form("add_med", clear_on_submit=True):
        name = st.text_input("Medicine name and dose (as on your label)")
        t = st.time_input("Daily time", dt.time(8, 0))
        if st.form_submit_button("Add") and name.strip():
            st.session_state.meds.append({"name": name.strip(), "time": t})
            st.session_state.meds.sort(key=lambda m: m["time"])
    now = dt.datetime.now().time()
    for i, m in enumerate(st.session_state.meds):
        a, b = st.columns([5, 1])
        a.markdown(f'<div class="card">💊 <b>{m["name"]}</b> at {m["time"].strftime("%I:%M %p")}</div>', unsafe_allow_html=True)
        if b.button("🗑", key=f"del{i}"):
            st.session_state.meds.pop(i)
            st.rerun()
    upcoming = [m for m in st.session_state.meds if m["time"] >= now]
    if upcoming:
        st.success(f"Next: {upcoming[0]['name']} at {upcoming[0]['time'].strftime('%I:%M %p')}")
    st.caption("Web apps can't send phone notifications when closed. For real alarms, use the Flutter version.")

elif page == PAGES[4]:
    st.title("Doctors & Clinics")
    st.caption("Sample listings. Replace with real doctors and clinics in your area.")
    for n, spec, clinic, hrs in DOCTORS:
        st.markdown(f'<div class="card">👩‍⚕️ <b>{n}</b> · {spec}<br>{clinic} · {hrs}</div>', unsafe_allow_html=True)

elif page == PAGES[5]:
    st.title("Health History")
    if not st.session_state.history:
        st.write("No records yet. Save symptoms from the Symptom Checker.")
    else:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download as CSV", df.to_csv(index=False), "health_history.csv", "text/csv")
        if st.button("Clear history"):
            st.session_state.history = []
            st.rerun()
    st.caption("Records are kept only for this browser session. Download them to keep a copy.")

else:
    st.title("Emergency Help 🚨")
    st.markdown('<div class="warn"><b>If you or someone else has any of these warning signs, call your local '
                'emergency number or go to the nearest hospital right away. Do not wait.</b></div>', unsafe_allow_html=True)
    for s in SIGNS:
        st.write(f"⚠️ {s}")
    st.info(DISCLAIMER)
