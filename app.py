# FREE PARETO TODO AGENT (NO TOKENS)
import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Free Pareto AI", page_icon="rocket", layout="centered")
st.title("Free Pareto To Do Agent")
st.markdown("**80/20 Rule • 100% Free • No Tokens**")

# === SIDEBAR ===
with st.sidebar:
    st.header("Free Setup")
    TASK_LIST_ID = st.text_input("To Do List ID", help="From Graph Explorer")
    st.caption("No AI key needed — uses free Grok on x.com")

if not TASK_LIST_ID:
    st.info("Paste your To Do List ID above.")
    st.stop()

# === GOAL INPUT ===
goal = st.text_input("Your Goal", placeholder="e.g., Get fit in 30 days")

if st.button("Generate FREE Pareto Tasks", type="primary"):
    if not goal:
        st.error("Enter a goal.")
    else:
    # === FREE AI: Use x.com Grok via manual copy-paste ===
        st.warning("**FREE AI MODE**")
        st.markdown("""
        1. Open [x.com](https://x.com) in another tab  
        2. Ask Grok:  
           ```
           Goal: {goal}
           Apply 80/20 rule. Give me 3–5 high-impact tasks as:
           1. Title - Description with [ ] checklist
           ```
        3. **Copy the full response**  
        4. Paste it below
        """.replace("{goal}", goal))

        user_paste = st.text_area("Paste Grok's response here:", height=200)
        if st.button("Use This Response"):
            if "1." not in user_paste:
                st.error("Response must contain numbered tasks (1., 2., etc.)")
            else:
                st.session_state.pareto_response = user_paste
                st.success("Tasks ready!")

# === SHOW TASKS ===
if "pareto_response" in st.session_state:
    st.markdown("### Your Pareto Tasks")
    st.code(st.session_state.pareto_response)

    if st.button("Create in Microsoft To Do", type="primary"):
        with st.spinner("Logging in..."):
            # Device login (free, no app registration)
            auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode"
            r = requests.post(auth_url, data={
                "client_id": "d3590ed6-52b3-4102-aeff-aad2292ab01c",
                "scope": "Tasks.ReadWrite offline_access"
            })
            resp = r.json()
            st.info(f"Go to: [{resp['verification_uri']}]({resp['verification_uri']})\nCode: `{resp['user_code']}`")
            if st.button("I signed in → Continue"):
                token_url = "https://login.microsoft.com/common/oauth2/v2.0/token"
                while True:
                    t = requests.post(token_url, data={
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "client_id": "d3590ed6-52b3-4102-aeff-aad2292ab01c",
                        "device_code": resp['device_code']
                    })
                    token = t.json()
                    if "access_token" in token:
                        token = token["access_token"]
                        st.success("Connected!")
                        break
                    elif token.get("error") != "authorization_pending":
                        st.error("Login failed.")
                        st.stop()

        # === CREATE TASKS ===
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT10:00:00")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        tasks = []
        for line in st.session_state.pareto_response.split("\n"):
            if line.strip() and line[0].isdigit():
                parts = line.split("-", 1)
                if len(parts) == 2:
                    title = parts[0].strip()[2:].strip()
                    desc = parts[1].strip()
                    tasks.append((title, desc))

        for title, desc in tasks:
            payload = {
                "title": title,
                "body": {"content": desc, "contentType": "text"},
                "importance": "high",
                "dueDateTime": {"dateTime": tomorrow, "timeZone": "Eastern Standard Time"},
                "isReminderOn": True,
                "categories": ["Pareto-80/20"]
            }
            url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{TASK_LIST_ID}/tasks"
            r = requests.post(url, headers=headers, json=payload)
            if r.status_code == 201:
                st.success(f"Created: {title}")
            else:
                st.error(f"Failed: {title}")

        st.balloons()
        st.markdown("**All tasks created in Microsoft To Do!**")

st.caption("Free forever • No AI tokens • Uses free Grok on x.com")
