import json
from deep_translator import GoogleTranslator
from datetime import datetime
import difflib

# Load data from JSON file
with open("boarding_data.json") as f:
    data = json.load(f)

translator = GoogleTranslator(source='auto', target='en')

print("🐶 Welcome to Scooby Pet Hostel! Ask me anything (Hindi/English).")

def parse_date(date_str):
    """
    Accepts date in formats like:
    - DD-MM-YYYY
    - DD/MM/YYYY
    - DD MM YYYY
    - DDMMYYYY
    """
    for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%d %m %Y", "%d%m%Y"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError("⚠️ Invalid date format. Please enter like 25-05-2026 or 25052026.")

while True:
    user_input = input("You: ")
    translated = translator.translate(user_input).lower()

    if "charge" in translated or "price" in translated or "paisa" in translated:
        print(f"Chatbot: 🐾 Charges are ₹{data['charges']['dog']}/day.")

    elif "time" in translated or "open" in translated or "timing" in translated:
        print(f"Chatbot: ⏰ We are open {data['timings']}.")

    elif "facility" in translated or "service" in translated:
        print("Chatbot: 🏠 Facilities include:\n- " + "\n- ".join(data['facilities']))

    elif "location" in translated or "address" in translated or "map" in translated:
        print(f"Chatbot: 📍 Location is {data['location']}\n🗺️ Map: {data['map_link']}")

    elif "book" in translated or "booking" in translated or "reserve" in translated:
        # Step 0: Ask about pet nature
        nature = input("Is your pet aggressive or friendly? ").strip().lower()

        # fuzzy match with difflib
        match = difflib.get_close_matches(nature, ["aggressive", "friendly"], n=1, cutoff=0.6)

        if match:
            if match[0] == "aggressive":
                print("Chatbot: ⚠️ Sorry, we can’t take aggressive pets because there is no cage system.")
                continue  # stop booking process here

            elif match[0] == "friendly":
                print("Chatbot: 🐾 Great! Welcome, let’s proceed with booking.")

                breed = input("Enter dog breed: ")

                # Flexible date input
                start_date_str = input("Enter start date (DDMMYYYY or DD-MM-YYYY): ")
                end_date_str = input("Enter end date (DDMMYYYY or DD-MM-YYYY): ")

                try:
                    start_date = parse_date(start_date_str)
                    end_date = parse_date(end_date_str)
                except ValueError as e:
                    print(e)
                    continue

                days = (end_date - start_date).days
                if days <= 0:
                    print("⚠️ Invalid dates. End date must be after start date.")
                    continue

                total = data['charges']['dog'] * days
                advance = 100
                remaining = total - advance

                # Step 1: Show charges + payment instruction
                print(f"\n💰 Total Charges: ₹{total}\n"
                      f"📅 Duration: {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')} ({days} days)\n"
                      f"🔑 For booking, please pay ₹{advance} advance via UPI: {data['payment_info']}\n"
                      f"👉 After payment, type 'paid' to confirm (⚠️ Demo only, actual PhonePe payment not verified).")

                # Step 2: Wait for user confirmation
                payment_confirm = input("You: ").lower()

                if "paid" in payment_confirm:
                    print(f"\n🎉 Successful Booking!\n"
                          f"🐶 Pet: {breed}\n"
                          f"📅 Duration: {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')} ({days} days)\n"
                          f"💰 Total Charges: ₹{total}\n"
                          f"🔑 Advance Paid: ₹{advance}\n"
                          f"💳 Remaining at Check-in: ₹{remaining}\n"
                          f"✅ Thank you! Your booking is confirmed.\n")
                else:
                    print("⚠️ Booking not confirmed. Advance payment required.")
        else:
            print("Chatbot: 🤔 Please specify clearly if your pet is 'aggressive' or 'friendly'.")

    elif "exit" in translated or "bye" in translated or "quit" in translated:
        print("Chatbot: Goodbye! 🐾 Have a great day!")
        break

    else:
        print("Chatbot: 🤔 Sorry, I didn’t understand. Try asking about charges, timings, facilities, booking, or location.")


