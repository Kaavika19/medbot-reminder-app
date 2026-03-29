import streamlit as st
from datetime import datetime
import platform

import threading
import random

# ---------------- BEEP SOUND ALERT ----------------
def beep_alert():
    if platform.system() == "Windows":
        import winsound
        def _run_beep():
            for _ in range(2):
                winsound.Beep(2000, 500)
        threading.Thread(target=_run_beep, daemon=True).start()

# ---------------- STREAMLIT SETUP ----------------
st.set_page_config(page_title="MedBot ", layout="centered")

# Initialize chat and reminders
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "Hi !!, I'm MedBot! "
        "I am here to take care your medicine timings."
        "\nType *add medicine* to begin or "
        "\nshow medicines to see your list"
        "\ntip for good health"}
    ]

if "reminders" not in st.session_state:
    st.session_state.reminders = []

# ---------------- CHAT DISPLAY ----------------
st.title("💊 MedBot - Medicine Reminder Assistant")

for msg in st.session_state.messages:
    st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

user_input = st.chat_input("Type your message...")

# ---------------- CHAT LOGIC ----------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    text = user_input.lower()
    response = ""

    if "add" in text and "medicine" in text:
        response = "Great! Enter like this:\n`Medicine Name Time(HH:MM) Dosage`\nExample:\nParacetamol 22:30 500mg"

    elif any(char.isdigit() for char in text):
        try:
            parts = text.split()
            name = parts[0].capitalize()
            time_str = parts[1]
            dose = parts[2] if len(parts) > 2 else "N/A"

            st.session_state.reminders.append({
                "name": name,
                "time": time_str,
                "dose": dose,
                "taken": False
            })
            response = f"Added reminder for *{name}* at *{time_str}* ({dose})."

        except:
            response = "⚠ Please use format like:\nAmoxicillin 18:00 250mg"

    elif "show" in text:
        if st.session_state.reminders:
            response = "Your Medicines:\n"
            for med in st.session_state.reminders:
                status = "Taken" if med["taken"] else "⏰ Pending"
                response += f"- {med['name']} at {med['time']} ({med['dose']}) — {status}\n"
        else:
            response = "You haven't added any medicines yet."

    elif "taken" in text:
        name = text.replace("taken", "").strip().capitalize()
        found = False
        for med in st.session_state.reminders:
            if med["name"].lower() == name.lower():
                med["taken"] = True
                found = True
                response = f"Marked *{name}* as taken."
        if not found:
            response = f"I couldn't find {name} in your list."

    elif "summary" in text:
        total = len(st.session_state.reminders)
        taken = sum(1 for m in st.session_state.reminders if m["taken"])
        response = f"Summary: {taken}/{total} medicines taken today."

    elif "tip" in text:
        tips = [
            " Drink enough water today!",
            " Consistency is key — take your medicine at the same time every day.",
            " Do not take medicine on an empty stomach unless prescribed.",
            " Proper rest speeds up recovery."
        ]
        response = random.choice(tips)

    else:
        response = "Need help? Try:\n- add medicine\n- show medicines\n- summary\n- tip"

    st.session_state.messages.append({"role": "bot", "content": response})
    st.rerun()

# ---------------- REMINDER CHECKER ----------------
current_time = datetime.now().strftime("%H:%M")

for index, med in enumerate(st.session_state.reminders):
    if med["time"] == current_time and not med["taken"]:

        # Popup + Toast
        st.toast(f"Time to take *{med['name']}* ({med['dose']})!")

        # PLAY BEEP SOUND 🎵
        beep_alert()

        # Sidebar alert with mark taken button
        with st.sidebar:
            st.warning(f"Please take *{med['name']}* now!")

            if st.button(f"Mark {med['name']} as Taken ", key=f"btn_{index}"):
                med["taken"] = True
                st.success(f"Marked *{med['name']}* as taken.")
                st.rerun()