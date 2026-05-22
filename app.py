import streamlit as st
import json
import difflib
from datetime import datetime
from dateutil import parser

# Load data
with open("boarding_data.json") as f:
    data = json.load(f)

# Title + Welcome
st.title("🐶 Welcome to Scooby Pet Hostel")
st.markdown("### Clear your doubts below 👇")

# Quick options
options = ["Charges", "Timings", "Facilities", "Location", "Booking"]
choice = st.selectbox("Choose a topic:", options)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = None
if "booking_info" not in st.session_state:
    st.session_state.booking_info = {}

# Show previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
user_input = st.chat_input("Type your message...")

# Fuzzy match for spelling mistakes
def fuzzy_match(user_input, keywords):
    words = user_input.lower().split()
    for word in words:
        match = difflib.get_close_matches(word, keywords, n=1, cutoff=0.7)
        if match:
            return match[0]
    return None

def parse_date_flexible(date_str):
    try:
        return parser.parse(date_str, dayfirst=True)
    except:
        return None

# Handle dropdown choice as user input
if choice and not user_input:
    user_input = choice

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    reply = ""
    keywords = ["charges", "timings", "facilities", "location", "booking", "friendly", "aggressive", "paid"]

    matched = fuzzy_match(user_input, keywords)

    # Normal queries
    if matched == "charges":
        reply = f"🐾 Charges are ₹{data['charges']['dog']}/day."

    elif matched == "timings":
        reply = f"⏰ We are open {data['timings']}."

    elif matched == "facilities":
        reply = "🏠 Facilities include:\n- " + "\n- ".join(data['facilities'])

    elif matched == "location":
        reply = f"📍 Location is {data['location']}\n🗺️ Map: {data['map_link']}"

    # Booking flow
    elif matched == "booking":
        st.session_state.step = "aggressive_friendly"
        reply = "🐶 Is your pet aggressive or friendly?"

    elif st.session_state.step == "aggressive_friendly":
        if matched == "aggressive":
            reply = "⚠️ Sorry, we can’t take because there is no cage system."
            st.session_state.step = None
        elif matched == "friendly":
            st.session_state.step = "breed"
            reply = "✅ Noted. What is the breed of your dog?"

    elif st.session_state.step == "breed":
        st.session_state.booking_info["breed"] = user_input
        st.session_state.step = "dog_name"
        reply = "🐕 Please tell me your dog's name."

    elif st.session_state.step == "dog_name":
        st.session_state.booking_info["dog_name"] = user_input
        st.session_state.step = "start_date"
        reply = "📅 Please enter the start date (any format)."

    elif st.session_state.step == "start_date":
        start_date = parse_date_flexible(user_input)
        if start_date:
            st.session_state.booking_info["start_date"] = start_date
            st.session_state.step = "end_date"
            reply = "📅 Great! Now please enter the end date (any format)."
        else:
            reply = "⚠️ Could not detect the start date. Please try again."

    elif st.session_state.step == "end_date":
        end_date = parse_date_flexible(user_input)
        if end_date:
            st.session_state.booking_info["end_date"] = end_date
            days = (end_date - st.session_state.booking_info["start_date"]).days
            total = data['charges']['dog'] * days
            advance = 100
            remaining = total - advance
            st.session_state.booking_info["days"] = days
            st.session_state.booking_info["total"] = total
            st.session_state.booking_info["advance"] = advance
            st.session_state.booking_info["remaining"] = remaining
            st.session_state.step = "payment"
            reply = (f"📅 Duration: {st.session_state.booking_info['start_date'].strftime('%d-%m-%Y')} "
                     f"to {end_date.strftime('%d-%m-%Y')} ({days} days)\n"
                     f"💰 Total Charges: ₹{total}\n"
                     f"🔑 Please pay ₹{advance} advance via UPI: {data['payment_info']}\n"
                     f"Type 'paid' after payment.")
        else:
            reply = "⚠️ Could not detect the end date. Please try again."

    elif st.session_state.step == "payment" and matched == "paid":
        info = st.session_state.booking_info
        reply = (f"🎉 Successful Booking! ✅\n"
                 f"🐕 Dog Breed: {info['breed']}\n"
                 f"🐶 Dog Name: {info['dog_name']}\n"
                 f"📅 Duration: {info['start_date'].strftime('%d-%m-%Y')} to {info['end_date'].strftime('%d-%m-%Y')} ({info['days']} days)\n"
                 f"💰 Total Charges: ₹{info['total']}\n"
                 f"🔑 Advance Paid: ₹{info['advance']}\n"
                 f"💵 Remaining: ₹{info['remaining']}\n"
                 f"✅ Thank you, your booking is confirmed.")
        st.session_state.step = None
        st.session_state.booking_info = {}

    else:
        reply = "🤔 Sorry, I didn’t understand. Try asking about charges, timings, facilities, booking, or location."

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)


