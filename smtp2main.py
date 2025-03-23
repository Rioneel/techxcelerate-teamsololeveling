import smtplib
import time
import pandas as pd
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import groq

# Groq API Key (Replace with actual key)
GROQ_API_KEY = "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"
client = groq.Client(api_key=GROQ_API_KEY)

# SMTP Configuration (Real Server)
SMTP_SERVER = "smtp.aspiredev.in"  # Replace with actual SMTP server
SMTP_PORT = 587  # Use 465 for SSL, 587 for TLS
SENDER_EMAIL = "no-reply-@aspiredev.in"
SENDER_PASSWORD = "S:_pw&>C:^$_cR2"  # Store securely, avoid hardcoding

lead_engagement = {}

def generate_email(username, ad_clicked):
    prompt = f"Write a professional yet engaging email for {username} about the ad they interacted with: {ad_clicked}."
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_email(recipient, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Authenticate
        server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        server.quit()
        
        # Update lead engagement score
        lead_engagement[recipient] = lead_engagement.get(recipient, 0) + 1
        print(f"Email sent to {recipient}, Engagement Score: {lead_engagement[recipient]}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def drip_campaign(leads_df):
    results = []
    
    for index, row in leads_df.iterrows():
        username, email, ad_clicked = row['username'], row['email'], row['ad_clicked_on']
        email_content = generate_email(username, ad_clicked)
        
        results.append({
            "username": username,
            "email": email,
            "ad_clicked_on": ad_clicked,
            "generated_email": email_content
        })
        
        send_email(email, "Your Personalized Ad Follow-Up", email_content)
        time.sleep(5)  # Delay between emails
    
    # Save generated emails to a CSV file
    results_df = pd.DataFrame(results)
    results_df.to_csv("generated_emails.csv", index=False)
    print("Generated emails saved to 'generated_emails.csv'")

    # AI-generated follow-ups based on engagement
    for email, score in lead_engagement.items():
        if score > 2:  # If lead has received multiple emails
            follow_up_email = "We noticed your interest! Here’s a special offer just for you."
            send_email(email, "Exclusive Offer Just for You!", follow_up_email)

# Streamlit UI
st.title("📩 AI-Powered Ad Engagement & Lead Nurturing System")
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data Preview:", df)
    
    if st.button("Start Drip Campaign"):
        drip_campaign(df)
        st.success("Drip campaign initiated! AI will monitor engagement and send follow-ups accordingly.")
        st.download_button("Download Generated Emails CSV", "generated_emails.csv", "text/csv")

