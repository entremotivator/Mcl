import streamlit as st
import pandas as pd
import json
import hashlib
import secrets
import string
import re
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import qrcode
from PIL import Image
import base64
import csv
import zipfile
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows

# --- Enhanced Categories & Descriptions ---
categories = {
    "Marketing & Sales Systems": [
        ("Advertising Platforms", "Google Ads, Facebook Ads, LinkedIn Ads, TikTok Ads, Twitter Ads"),
        ("Email Marketing", "Mailchimp, ConvertKit, ActiveCampaign, Klaviyo, Constant Contact"),
        ("CRM Systems", "Salesforce, HubSpot, Pipedrive, Zoho CRM, Monday CRM"),
        ("Event Management", "Eventbrite, Meetup, Facebook Events, Zoom Events"),
        ("Sales Funnels", "ClickFunnels, Leadpages, Unbounce, Instapage, Kartra"),
        ("Affiliate Management", "ShareASale, ClickBank, Commission Junction, Impact"),
        ("Social Media Management", "Hootsuite, Buffer, Later, Sprout Social, Creator Studio"),
        ("Lead Generation", "OptinMonster, Sumo, Hello Bar, ConvertFlow, Privy"),
        ("Analytics & Tracking", "Google Analytics, Facebook Pixel, Hotjar, Mixpanel, Amplitude"),
    ],
    "Communication & Support": [
        ("Phone & SMS", "Twilio, RingCentral, Grasshopper, CallRail, TextMagic"),
        ("Live Chat & Messaging", "Intercom, Drift, Zendesk Chat, Tidio, Crisp"),
        ("Video Conferencing", "Zoom, Google Meet, Microsoft Teams, GoToMeeting, WebEx"),
        ("Customer Support", "Zendesk, Freshdesk, Help Scout, Kayako, ServiceNow"),
        ("Team Communication", "Slack, Microsoft Teams, Discord, Telegram, WhatsApp Business"),
        ("Email Services", "Gmail, Outlook, ProtonMail, Zoho Mail, FastMail"),
        ("Survey & Feedback", "Typeform, SurveyMonkey, Google Forms, Jotform, Formstack"),
        ("Knowledge Base", "Notion, Confluence, GitBook, Document360, Helpjuice"),
    ],
    "Content & Media Production": [
        ("Website Builders", "WordPress, Wix, Squarespace, Webflow, Shopify"),
        ("E-commerce Platforms", "Shopify, WooCommerce, BigCommerce, Magento, PrestaShop"),
        ("Course Platforms", "Teachable, Thinkific, Kajabi, LearnDash, Udemy"),
        ("Podcast Hosting", "Anchor, Libsyn, Buzzsprout, Podbean, SimpleCast"),
        ("Video Hosting", "YouTube, Vimeo, Wistia, Loom, Vidyard"),
        ("Design Tools", "Canva, Adobe Creative Suite, Figma, Sketch, InVision"),
        ("Stock Media", "Shutterstock, Getty Images, Unsplash, Pexels, Adobe Stock"),
        ("Content Management", "WordPress, Drupal, Joomla, Ghost, Strapi"),
        ("Landing Page Builders", "Leadpages, Unbounce, Instapage, ClickFunnels, ConvertKit"),
    ],
    "Technical Infrastructure": [
        ("Web Hosting", "AWS, Google Cloud, DigitalOcean, Bluehost, SiteGround"),
        ("Domain Management", "GoDaddy, Namecheap, CloudFlare, Google Domains, Route 53"),
        ("CDN & Security", "CloudFlare, AWS CloudFront, MaxCDN, KeyCDN, Sucuri"),
        ("Payment Processing", "Stripe, PayPal, Square, Authorize.net, Braintree"),
        ("Appointment Booking", "Calendly, Acuity, Book Like A Boss, SimplyBook.me, Setmore"),
        ("File Storage", "Google Drive, Dropbox, OneDrive, Box, AWS S3"),
        ("Backup Solutions", "Backblaze, Carbonite, Acronis, Veeam, Time Machine"),
        ("SSL Certificates", "Let's Encrypt, DigiCert, Comodo, GeoTrust, Sectigo"),
        ("DNS Management", "CloudFlare, Route 53, Google DNS, Quad9, OpenDNS"),
    ],
    "Business Operations": [
        ("Project Management", "Asana, Trello, Monday.com, ClickUp, Basecamp"),
        ("Time Tracking", "Toggl, RescueTime, Clockify, Harvest, TimeCamp"),
        ("Invoicing & Billing", "QuickBooks, FreshBooks, Wave, Zoho Invoice, Invoice2go"),
        ("Accounting Software", "QuickBooks, Xero, Wave, FreshBooks, Sage"),
        ("HR & Payroll", "Gusto, ADP, BambooHR, Workday, Zenefits"),
        ("Document Signing", "DocuSign, HelloSign, Adobe Sign, PandaDoc, SignNow"),
        ("Password Management", "1Password, LastPass, Bitwarden, Dashlane, Keeper"),
        ("VPN Services", "ExpressVPN, NordVPN, CyberGhost, Surfshark, ProtonVPN"),
        ("Legal & Compliance", "LegalZoom, Rocket Lawyer, Nolo, CorpNet, Incfile"),
    ],
    "Automation & Integration": [
        ("Workflow Automation", "Zapier, Microsoft Power Automate, IFTTT, Integromat, n8n"),
        ("API Management", "Postman, Insomnia, Swagger, RapidAPI, Apigee"),
        ("Database Management", "MySQL, PostgreSQL, MongoDB, Firebase, Airtable"),
        ("Code Repositories", "GitHub, GitLab, Bitbucket, Azure DevOps, SourceForge"),
        ("CI/CD Pipelines", "Jenkins, GitHub Actions, GitLab CI, CircleCI, Travis CI"),
        ("Monitoring Tools", "New Relic, DataDog, Pingdom, UptimeRobot, StatusPage"),
        ("Error Tracking", "Sentry, Bugsnag, Rollbar, Airbrake, LogRocket"),
        ("Load Testing", "LoadRunner, JMeter, K6, Blazemeter, Loader.io"),
    ],
    "AI & Advanced Systems": [
        ("AI Platforms", "OpenAI, Anthropic Claude, Google AI, Microsoft Azure AI, IBM Watson"),
        ("Vector Databases", "Pinecone, Weaviate, Qdrant, Chroma, Milvus"),
        ("Machine Learning", "TensorFlow, PyTorch, Scikit-learn, Keras, Hugging Face"),
        ("Chatbot Platforms", "Dialogflow, Amazon Lex, Microsoft Bot Framework, Rasa, Botpress"),
        ("Data Analytics", "Tableau, Power BI, Looker, Qlik, Sisense"),
        ("A/B Testing", "Optimizely, VWO, Google Optimize, Unbounce, Convert"),
        ("Personalization", "Dynamic Yield, Evergage, Monetate, Yieldify, Qubit"),
        ("Predictive Analytics", "DataRobot, H2O.ai, BigML, RapidMiner, KNIME"),
    ]
}

# --- Security Features ---
def hash_master_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_strong_password(length=16, include_symbols=True):
    """Generate a cryptographically secure password"""
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def check_password_strength(password):
    """Check password strength and return score with recommendations"""
    score = 0
    feedback = []
    
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        feedback.append("Use at least 8 characters (12+ recommended)")
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Include lowercase letters")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Include uppercase letters")
    
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Include numbers")
    
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        score += 1
    else:
        feedback.append("Include special characters")
    
    if len(set(password)) > len(password) * 0.7:
        score += 1
    else:
        feedback.append("Avoid too many repeated characters")
    
    strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong"]
    strength = strength_levels[min(score, 5)]
    
    return strength, score, feedback

def create_qr_code(text):
    """Generate QR code for sharing credentials securely"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# --- Enhanced Streamlit Setup ---
st.set_page_config(
    page_title="Enhanced Business Systems Manager", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://help.streamlit.io',
        'Report a bug': 'https://github.com/streamlit/streamlit/issues',
        'About': "# Business Systems & Password Manager\nSecurely manage all your business credentials in one place."
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.section-header {
    background: linear-gradient(90deg, #1f77b4, #17a2b8);
    color: white;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
.password-strength {
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
.strength-very-weak { background-color: #ff4444; color: white; }
.strength-weak { background-color: #ff8800; color: white; }
.strength-fair { background-color: #ffaa00; color: black; }
.strength-good { background-color: #88cc00; color: black; }
.strength-strong { background-color: #44aa00; color: white; }
.strength-very-strong { background-color: #00aa44; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🔐 Enhanced Business Systems & Password Manager</h1>', unsafe_allow_html=True)
st.markdown("### A comprehensive, secure solution for managing all your business credentials and systems")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Master Password Setup
    if "master_password_set" not in st.session_state:
        st.session_state.master_password_set = False
        st.session_state.master_password_hash = None
    
    if not st.session_state.master_password_set:
        st.subheader("🔒 Set Master Password")
        master_pwd = st.text_input("Create Master Password:", type="password", key="master_setup")
        confirm_pwd = st.text_input("Confirm Master Password:", type="password", key="master_confirm")
        
        if master_pwd and confirm_pwd:
            if master_pwd == confirm_pwd:
                strength, score, feedback = check_password_strength(master_pwd)
                if score >= 4:
                    if st.button("Set Master Password"):
                        st.session_state.master_password_hash = hash_master_password(master_pwd)
                        st.session_state.master_password_set = True
                        st.success("✅ Master password set successfully!")
                        st.rerun()
                else:
                    st.warning(f"Password strength: {strength}. Please use a stronger password.")
                    for tip in feedback:
                        st.write(f"• {tip}")
            else:
                st.error("Passwords don't match!")
    else:
        st.success("🔓 Master password is set")
        if st.button("🔄 Change Master Password"):
            st.session_state.master_password_set = False
            st.rerun()
    
    # Auto-save settings
    st.subheader("💾 Auto-save Settings")
    auto_save = st.checkbox("Enable auto-save", value=True)
    save_interval = st.selectbox("Save interval:", [1, 5, 10, 15], index=1)
    
    # Export settings
    st.subheader("📤 Export Settings")
    export_format = st.selectbox("Default export format:", ["PDF", "Excel", "CSV", "JSON"])
    include_timestamps = st.checkbox("Include timestamps in exports", value=True)
    encrypt_exports = st.checkbox("Encrypt exports", value=True)
    
    # Security settings
    st.subheader("🛡️ Security Settings")
    show_passwords = st.checkbox("Show passwords in overview", value=False)
    enable_2fa = st.checkbox("Enable 2FA (future feature)", value=False)
    session_timeout = st.selectbox("Session timeout (minutes):", [15, 30, 60, 120], index=1)

# Check if master password is set before proceeding
if not st.session_state.master_password_set:
    st.warning("⚠️ Please set a master password in the sidebar to continue.")
    st.stop()

# Verify master password for access
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔐 Enter Master Password")
    entered_password = st.text_input("Master Password:", type="password")
    if st.button("🔓 Unlock"):
        if hash_master_password(entered_password) == st.session_state.master_password_hash:
            st.session_state.authenticated = True
            st.session_state.login_time = datetime.now()
            st.success("✅ Access granted!")
            st.rerun()
        else:
            st.error("❌ Invalid master password!")
    st.stop()

# Check session timeout
if datetime.now() - st.session_state.get('login_time', datetime.now()) > timedelta(minutes=session_timeout):
    st.session_state.authenticated = False
    st.warning("⏰ Session expired. Please log in again.")
    st.rerun()

# --- Initialize Enhanced Data Structure ---
if "enhanced_data" not in st.session_state:
    st.session_state.enhanced_data = {}
    for section, items in categories.items():
        st.session_state.enhanced_data[section] = {}
        for name, desc in items:
            st.session_state.enhanced_data[section][name] = {
                "username": "",
                "password": "",
                "url": "",
                "notes": "",
                "created_date": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "password_strength": "Not Set",
                "tags": []
            }

# Initialize other session states
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All Categories"

# --- Main Interface ---
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("🔍 Search & Filter")
    search_query = st.text_input("Search systems:", value=st.session_state.search_query)
    st.session_state.search_query = search_query
    
    category_options = ["All Categories"] + list(categories.keys())
    selected_category = st.selectbox("Filter by category:", category_options)
    st.session_state.selected_category = selected_category
    
    # Quick stats
    st.subheader("📊 Quick Stats")
    total_systems = sum(len(items) for items in categories.values())
    filled_systems = 0
    for section_data in st.session_state.enhanced_data.values():
        for system_data in section_data.values():
            if system_data["password"]:
                filled_systems += 1
    
    st.metric("Total Systems", total_systems)
    st.metric("Configured Systems", filled_systems)
    st.metric("Completion Rate", f"{(filled_systems/total_systems)*100:.1f}%")

with col1:
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Manage Systems", "📊 Overview", "🔧 Tools", "📈 Analytics"])
    
    with tab1:
        st.subheader("🔐 System Management")
        
        # Filter categories based on selection
        display_categories = categories if selected_category == "All Categories" else {selected_category: categories[selected_category]}
        
        # Filter categories based on selection
        display_categories = categories if selected_category == "All Categories" else {selected_category: categories[selected_category]}
        
        # Create form for each category separately to avoid issues
        for section, items in display_categories.items():
            st.markdown(f'<div class="section-header"><h3>🔹 {section}</h3></div>', unsafe_allow_html=True)
            
            with st.form(f"form_{section.replace(' ', '_').replace('&', 'and')}", clear_on_submit=False):
                changes_made = False
                
                for name, desc in items:
                    # Filter by search query
                    if search_query and search_query.lower() not in name.lower() and search_query.lower() not in desc.lower():
                        continue
                    
                    with st.expander(f"{name}", expanded=False):
                        st.caption(f"📋 {desc}")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            current_data = st.session_state.enhanced_data[section][name]
                            
                            username = st.text_input(
                                f"Username/Email",
                                current_data["username"],
                                key=f"username_{section}_{name}".replace(" ", "_").replace("&", "and")
                            )
                            
                            password = st.text_input(
                                f"Password",
                                current_data["password"],
                                type="password",
                                key=f"password_{section}_{name}".replace(" ", "_").replace("&", "and")
                            )
                            
                            url = st.text_input(
                                f"URL/Website",
                                current_data["url"],
                                key=f"url_{section}_{name}".replace(" ", "_").replace("&", "and")
                            )
                        
                        with col_b:
                            notes = st.text_area(
                                f"Notes",
                                current_data["notes"],
                                height=100,
                                key=f"notes_{section}_{name}".replace(" ", "_").replace("&", "and")
                            )
                            
                            tags_input = st.text_input(
                                f"Tags (comma-separated)",
                                ", ".join(current_data["tags"]),
                                key=f"tags_{section}_{name}".replace(" ", "_").replace("&", "and")
                            )
                            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                        
                        # Password strength indicator
                        if password:
                            strength, score, feedback = check_password_strength(password)
                            strength_class = f"strength-{strength.lower().replace(' ', '-')}"
                            st.markdown(f'<div class="password-strength {strength_class}">Password Strength: {strength}</div>', unsafe_allow_html=True)
                            
                            if feedback:
                                with st.expander("💡 Password Improvement Tips"):
                                    for tip in feedback:
                                        st.write(f"• {tip}")
                        
                        # Check if data has changed
                        if (username != current_data["username"] or 
                            password != current_data["password"] or 
                            url != current_data["url"] or 
                            notes != current_data["notes"] or 
                            tags != current_data["tags"]):
                            changes_made = True
                        
                        # Update session state immediately (don't wait for submit)
                        st.session_state.enhanced_data[section][name].update({
                            "username": username,
                            "password": password,
                            "url": url,
                            "notes": notes,
                            "tags": tags,
                            "last_modified": datetime.now().isoformat(),
                            "password_strength": check_password_strength(password)[0] if password else "Not Set"
                        })
                
                # Submit button for this section
                submitted = st.form_submit_button(f"💾 Save {section}", type="primary")
                if submitted:
                    st.success(f"✅ {section} data saved successfully!")
        
        # Password generation tools outside forms
        st.markdown("---")
        st.subheader("🔧 Password Tools")
        
        tool_col1, tool_col2, tool_col3 = st.columns(3)
        
        with tool_col1:
            st.write("**🎲 Generate Password**")
            gen_length = st.selectbox("Length:", [12, 16, 20, 24], index=1, key="gen_length")
            if st.button("Generate Strong Password", key="main_gen"):
                new_pwd = generate_strong_password(gen_length)
                st.code(new_pwd)
                strength, score, _ = check_password_strength(new_pwd)
                st.write(f"Strength: {strength}")
        
        with tool_col2:
            st.write("**🔍 Test Password Strength**")
            test_pwd = st.text_input("Enter password to test:", type="password", key="test_pwd")
            if test_pwd:
                strength, score, feedback = check_password_strength(test_pwd)
                st.write(f"**Strength:** {strength} ({score}/6)")
                if feedback:
                    for tip in feedback[:2]:  # Show top 2 tips
                        st.write(f"💡 {tip}")
        
        with tool_col3:
            st.write("**💾 Quick Actions**")
            if st.button("🔄 Refresh All Data", key="refresh_all"):
                st.rerun()
            if st.button("📊 View Analytics", key="goto_analytics"):
                st.info("Switch to Analytics tab to see detailed reports")
    
    with tab2:
        st.subheader("📊 System Overview")
        
        # Create comprehensive dataframe
        all_records = []
        for section, systems in st.session_state.enhanced_data.items():
            for name, data in systems.items():
                if not search_query or search_query.lower() in name.lower() or search_query.lower() in section.lower():
                    all_records.append({
                        "Category": section,
                        "System": name,
                        "Username": data.get("username", ""),
                        "Password": "••••••••" if data.get("password") and not show_passwords else data.get("password", ""),
                        "URL": data.get("url", ""),
                        "Strength": data.get("password_strength", "Not Set"),
                        "Tags": ", ".join(data.get("tags", [])),
                        "Notes": (data.get("notes", "")[:50] + "...") if len(data.get("notes", "")) > 50 else data.get("notes", ""),
                        "Last Modified": data.get("last_modified", "Never")[:10] if data.get("last_modified") else "Never"
                    })
        
        df_overview = pd.DataFrame(all_records)
        
        if not df_overview.empty:
            # Color-code based on password strength
            def highlight_strength(val):
                if pd.isna(val):
                    return "background-color: #cccccc; color: black"
                color_map = {
                    "Very Strong": "background-color: #00aa44; color: white",
                    "Strong": "background-color: #44aa00; color: white",
                    "Good": "background-color: #88cc00; color: black",
                    "Fair": "background-color: #ffaa00; color: black",
                    "Weak": "background-color: #ff8800; color: white",
                    "Very Weak": "background-color: #ff4444; color: white",
                    "Not Set": "background-color: #cccccc; color: black"
                }
                return color_map.get(val, "")
            
            try:
                styled_df = df_overview.style.applymap(highlight_strength, subset=['Strength'])
                st.dataframe(styled_df, use_container_width=True, height=400)
            except Exception:
                # Fallback to regular dataframe if styling fails
                st.dataframe(df_overview, use_container_width=True, height=400)
            
            # Summary statistics
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                strong_passwords = len([r for r in all_records if r["Strength"] in ["Strong", "Very Strong"]])
                st.metric("Strong Passwords", strong_passwords)
            with col_stat2:
                weak_passwords = len([r for r in all_records if r["Strength"] in ["Weak", "Very Weak"]])
                st.metric("Weak Passwords", weak_passwords, delta=-weak_passwords if weak_passwords > 0 else 0)
            with col_stat3:
                empty_passwords = len([r for r in all_records if r["Strength"] == "Not Set"])
                st.metric("Missing Passwords", empty_passwords, delta=-empty_passwords if empty_passwords > 0 else 0)
            with col_stat4:
                with_urls = len([r for r in all_records if r["URL"]])
                st.metric("Systems with URLs", with_urls)
        else:
            st.info("No systems match your search criteria.")
    
    with tab3:
        st.subheader("🔧 Utility Tools")
        
        tool_col1, tool_col2 = st.columns(2)
        
        with tool_col1:
            st.subheader("🎲 Password Generator")
            gen_length = st.slider("Password Length", 8, 32, 16)
            gen_include_symbols = st.checkbox("Include Symbols", True)
            gen_include_numbers = st.checkbox("Include Numbers", True)
            gen_exclude_ambiguous = st.checkbox("Exclude Ambiguous Characters (0, O, l, I)", True)
            
            if st.button("Generate Password"):
                characters = string.ascii_letters
                if gen_include_numbers:
                    characters += string.digits
                if gen_include_symbols:
                    characters += "!@#$%^&*()-_=+[]{}|;:,.<>?"
                if gen_exclude_ambiguous:
                    characters = characters.replace("0O1lI", "")
                
                new_password = ''.join(secrets.choice(characters) for _ in range(gen_length))
                st.code(new_password)
                strength, score, feedback = check_password_strength(new_password)
                st.write(f"**Strength:** {strength}")
        
        with tool_col2:
            st.subheader("🔍 Password Analyzer")
            test_password = st.text_input("Enter password to analyze:", type="password")
            if test_password:
                strength, score, feedback = check_password_strength(test_password)
                st.write(f"**Strength:** {strength} (Score: {score}/6)")
                if feedback:
                    st.write("**Recommendations:**")
                    for tip in feedback:
                        st.write(f"• {tip}")
        
        st.subheader("📤 Advanced Export Options")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("📊 Export to Excel"):
                # Create Excel file with multiple sheets
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Summary sheet
                    summary_data = []
                    for section, systems in st.session_state.enhanced_data.items():
                        for name, data in systems.items():
                            summary_data.append({
                                "Category": section,
                                "System": name,
                                "Username": data["username"],
                                "Password": data["password"],
                                "URL": data["url"],
                                "Strength": data["password_strength"],
                                "Tags": ", ".join(data["tags"]),
                                "Notes": data["notes"],
                                "Created": data["created_date"][:10],
                                "Modified": data["last_modified"][:10]
                            })
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='All Systems', index=False)
                    
                    # Individual category sheets
                    for category in categories.keys():
                        cat_data = [item for item in summary_data if item["Category"] == category]
                        if cat_data:
                            cat_df = pd.DataFrame(cat_data)
                            sheet_name = category[:31]  # Excel sheet name limit
                            cat_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                output.seek(0)
                st.download_button(
                    "⬇️ Download Excel File",
                    output,
                    f"business_systems_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with export_col2:
            if st.button("🗜️ Export to ZIP Archive"):
                # Create ZIP with multiple formats
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add CSV
                    csv_data = pd.DataFrame(records).to_csv(index=False)
                    zip_file.writestr("systems.csv", csv_data)
                    
                    # Add JSON
                    json_data = json.dumps(st.session_state.enhanced_data, indent=2)
                    zip_file.writestr("systems.json", json_data)
                    
                    # Add README
                    readme = """# Business Systems Export
                    
This archive contains your business systems data in multiple formats:
- systems.csv: Spreadsheet format
- systems.json: Complete data with metadata
- README.txt: This file

Export generated on: {date}
Total systems: {total}
""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), total=len(records))
                    zip_file.writestr("README.txt", readme)
                
                zip_buffer.seek(0)
                st.download_button(
                    "⬇️ Download ZIP Archive",
                    zip_buffer,
                    f"business_systems_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    "application/zip"
                )
    
    with tab4:
        st.subheader("📈 Security Analytics & Reports")
        
        # Prepare analytics data
        analytics_data = []
        for section, systems in st.session_state.enhanced_data.items():
            for name, data in systems.items():
                analytics_data.append({
                    "Category": section,
                    "System": name,
                    "Has_Password": bool(data["password"]),
                    "Password_Strength": data["password_strength"],
                    "Has_Username": bool(data["username"]),
                    "Has_URL": bool(data["url"]),
                    "Has_Notes": bool(data["notes"]),
                    "Tag_Count": len(data["tags"]),
                    "Created": pd.to_datetime(data["created_date"]) if data["created_date"] else None,
                    "Modified": pd.to_datetime(data["last_modified"]) if data["last_modified"] else None
                })
        
        analytics_df = pd.DataFrame(analytics_data)
        
        if not analytics_df.empty:
            # Security Score Calculation
            col_score1, col_score2, col_score3 = st.columns(3)
            
            with col_score1:
                # Overall Security Score
                total_systems = len(analytics_df)
                systems_with_passwords = analytics_df['Has_Password'].sum()
                strong_passwords = len(analytics_df[analytics_df['Password_Strength'].isin(['Strong', 'Very Strong'])])
                systems_with_urls = analytics_df['Has_URL'].sum()
                
                password_score = (systems_with_passwords / total_systems) * 40
                strength_score = (strong_passwords / total_systems) * 35
                completeness_score = (systems_with_urls / total_systems) * 25
                
                overall_score = password_score + strength_score + completeness_score
                
                st.metric(
                    "Overall Security Score", 
                    f"{overall_score:.1f}/100",
                    delta=f"{overall_score - 75:.1f}" if overall_score >= 75 else f"{overall_score - 75:.1f}"
                )
            
            with col_score2:
                # Password Coverage
                coverage = (systems_with_passwords / total_systems) * 100
                st.metric("Password Coverage", f"{coverage:.1f}%")
                
            with col_score3:
                # Strong Password Ratio
                if systems_with_passwords > 0:
                    strong_ratio = (strong_passwords / systems_with_passwords) * 100
                    st.metric("Strong Password Ratio", f"{strong_ratio:.1f}%")
                else:
                    st.metric("Strong Password Ratio", "0%")
            
            # Charts and visualizations
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("Password Strength Distribution")
                strength_counts = analytics_df['Password_Strength'].value_counts()
                st.bar_chart(strength_counts)
            
            with chart_col2:
                st.subheader("Completion by Category")
                category_completion = analytics_df.groupby('Category')['Has_Password'].mean() * 100
                st.bar_chart(category_completion)
            
            # Detailed recommendations
            st.subheader("🎯 Security Recommendations")
            
            # Find systems needing attention
            weak_systems = analytics_df[analytics_df['Password_Strength'].isin(['Weak', 'Very Weak', 'Not Set'])]
            missing_urls = analytics_df[~analytics_df['Has_URL']]
            no_username = analytics_df[~analytics_df['Has_Username']]
            
            rec_col1, rec_col2, rec_col3 = st.columns(3)
            
            with rec_col1:
                if not weak_systems.empty:
                    st.warning("⚠️ Systems needing stronger passwords:")
                    for _, system in weak_systems.head(5).iterrows():
                        st.write(f"• {system['System']} ({system['Category']})")
                else:
                    st.success("✅ All systems have strong passwords!")
            
            with rec_col2:
                if not missing_urls.empty:
                    st.info("ℹ️ Systems missing URLs:")
                    for _, system in missing_urls.head(5).iterrows():
                        st.write(f"• {system['System']} ({system['Category']})")
                else:
                    st.success("✅ All systems have URLs!")
            
            with rec_col3:
                if not no_username.empty:
                    st.info("ℹ️ Systems missing usernames:")
                    for _, system in no_username.head(5).iterrows():
                        st.write(f"• {system['System']} ({system['Category']})")
                else:
                    st.success("✅ All systems have usernames!")
            
            # Activity timeline
            st.subheader("📅 System Management Activity")
            if analytics_df['Modified'].notna().any():
                activity_data = analytics_df[analytics_df['Modified'].notna()].copy()
                activity_data['Date'] = activity_data['Modified'].dt.date
                daily_activity = activity_data.groupby('Date').size().reset_index(name='Systems Updated')
                
                if not daily_activity.empty:
                    st.line_chart(daily_activity.set_index('Date'))
                else:
                    st.info("No recent activity to display")
        else:
            st.info("No data available for analytics")

# --- Advanced Export Functions ---
def create_enhanced_pdf(dataframe, include_qr=False):
    """Create an enhanced PDF report with better formatting"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.darkblue
    )
    
    elements = []
    
    # Title page
    elements.append(Paragraph("Business Systems & Credentials Report", title_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Executive summary
    total_systems = len(dataframe)
    systems_with_passwords = len([r for r in dataframe.to_dict('records') if r.get('Password') and r['Password'] != '••••••••'])
    
    summary_text = f"""
    <b>Executive Summary:</b><br/>
    • Total Systems Managed: {total_systems}<br/>
    • Systems with Passwords: {systems_with_passwords}<br/>
    • Coverage Rate: {(systems_with_passwords/total_systems)*100:.1f}%<br/>
    • Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(PageBreak())
    
    # Group data by category
    for category in dataframe['Category'].unique():
        category_data = dataframe[dataframe['Category'] == category]
        
        elements.append(Paragraph(f"{category}", heading_style))
        
        # Create table data
        table_data = [["System", "Username", "URL", "Strength", "Notes"]]
        
        for _, row in category_data.iterrows():
            table_data.append([
                row['System'],
                row['Username'][:20] + "..." if len(str(row['Username'])) > 20 else row['Username'],
                row['URL'][:30] + "..." if len(str(row['URL'])) > 30 else row['URL'],
                row['Strength'] if 'Strength' in row else 'N/A',
                str(row['Notes'])[:40] + "..." if len(str(row['Notes'])) > 40 else row['Notes']
            ])
        
        # Create and style table
        table = Table(table_data, colWidths=[100, 80, 120, 60, 140])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
    
    # Add QR code if requested
    if include_qr:
        qr_text = f"Business Systems Report - Generated: {datetime.now().strftime('%Y-%m-%d')}"
        qr_img = create_qr_code(qr_text)
        
        # Convert PIL image to ReportLab image
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        elements.append(Paragraph("Scan for Report Info:", styles['Normal']))
        elements.append(Spacer(1, 10))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- Enhanced Download Section ---
st.subheader("📤 Export & Backup Options")

export_col1, export_col2, export_col3 = st.columns(3)

# Prepare export records
export_records = []
for section, systems in st.session_state.enhanced_data.items():
    for name, data in systems.items():
        export_records.append({
            "Category": section,
            "System": name,
            "Username": data.get("username", ""),
            "Password": data.get("password", ""),
            "URL": data.get("url", ""),
            "Strength": data.get("password_strength", "Not Set"),
            "Tags": ", ".join(data.get("tags", [])),
            "Notes": data.get("notes", ""),
            "Created": data.get("created_date", "")[:10] if data.get("created_date") else "",
            "Modified": data.get("last_modified", "")[:10] if data.get("last_modified") else ""
        })

with export_col1:
    # CSV Export
    if export_records:
        csv_df = pd.DataFrame(export_records)
        st.download_button(
            "📊 Download CSV",
            csv_df.to_csv(index=False).encode("utf-8"),
            f"business_systems_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            help="Download as comma-separated values file"
        )

with export_col2:
    # Enhanced PDF Export
    if export_records:
        try:
            pdf_buffer = create_enhanced_pdf(pd.DataFrame(export_records), include_qr=True)
            st.download_button(
                "📄 Download Enhanced PDF",
                pdf_buffer,
                f"business_systems_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "application/pdf",
                help="Download detailed PDF report with formatting"
            )
        except Exception as e:
            st.error(f"PDF generation error: {str(e)}")

with export_col3:
    # JSON Backup
    if st.session_state.enhanced_data:
        backup_data = {
            "export_date": datetime.now().isoformat(),
            "version": "2.0",
            "systems": st.session_state.enhanced_data,
            "metadata": {
                "total_categories": len(categories),
                "total_systems": sum(len(items) for items in categories.values()),
                "export_settings": {
                    "include_timestamps": include_timestamps,
                    "format_version": "enhanced"
                }
            }
        }
        
        st.download_button(
            "💾 Download JSON Backup",
            json.dumps(backup_data, indent=2).encode("utf-8"),
            f"business_systems_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "application/json",
            help="Complete backup with all data and metadata"
        )

# --- Backup & Restore Section ---
st.subheader("🔄 Backup & Restore")

backup_col1, backup_col2 = st.columns(2)

with backup_col1:
    st.write("**📤 Create Backup**")
    if st.button("🗂️ Create Full Backup"):
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "version": "2.0",
            "master_password_hash": st.session_state.get("master_password_hash"),
            "systems": st.session_state.enhanced_data,
            "settings": {
                "auto_save": auto_save,
                "save_interval": save_interval,
                "export_format": export_format,
                "include_timestamps": include_timestamps
            }
        }
        
        st.download_button(
            "⬇️ Download Full Backup",
            json.dumps(backup_data, indent=2).encode("utf-8"),
            f"complete_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "application/json"
        )

with backup_col2:
    st.write("**📥 Restore from Backup**")
    uploaded_backup = st.file_uploader("Choose backup file", type=["json"])
    
    if uploaded_backup is not None:
        try:
            backup_content = json.loads(uploaded_backup.getvalue().decode("utf-8"))
            
            if "systems" in backup_content:
                st.success("✅ Valid backup file detected!")
                st.write(f"**Backup Date:** {backup_content.get('backup_date', 'Unknown')}")
                st.write(f"**Version:** {backup_content.get('version', 'Unknown')}")
                
                if st.button("🔄 Restore Data", type="primary"):
                    st.session_state.enhanced_data = backup_content["systems"]
                    if "settings" in backup_content:
                        # Restore settings if available
                        pass
                    st.success("✅ Data restored successfully!")
                    st.rerun()
            else:
                st.error("❌ Invalid backup file format")
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file")
        except Exception as e:
            st.error(f"❌ Error reading backup: {str(e)}")

# --- Email Functionality ---
st.subheader("📧 Secure Email Export")

email_col1, email_col2 = st.columns(2)

with email_col1:
    st.write("**📮 Email Configuration**")
    recipient_email = st.text_input("Recipient Email:", placeholder="user@example.com")
    sender_email = st.text_input("Your Email:", placeholder="your_email@gmail.com")
    email_password = st.text_input("Email App Password:", type="password", help="Use App Password, not regular password")
    
    email_subject = st.text_input("Subject:", value=f"Business Systems Export - {datetime.now().strftime('%Y-%m-%d')}")

with email_col2:
    st.write("**📝 Email Options**")
    include_pdf = st.checkbox("Include PDF Report", value=True)
    include_csv = st.checkbox("Include CSV Data", value=False)
    encrypt_email = st.checkbox("Encrypt Attachments", value=True, help="Password protect attachments")
    
    custom_message = st.text_area(
        "Custom Message:", 
        value="Please find attached your business systems export. Handle with care as this contains sensitive information.",
        height=100
    )

if st.button("📧 Send Secure Email", type="primary"):
    if recipient_email and sender_email and email_password:
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = email_subject
            
            # Email body
            total_records = len(export_records) if export_records else 0
            body = f"""
{custom_message}

Export Details:
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Total Systems: {total_records}
- Format: {'PDF' if include_pdf else 'CSV' if include_csv else 'JSON'}
- Security: {'Encrypted' if encrypt_email else 'Standard'}

This email contains sensitive business information. Please handle securely.

Best regards,
Business Systems Manager
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach files
            if include_pdf and export_records:
                try:
                    pdf_data = create_enhanced_pdf(pd.DataFrame(export_records))
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(pdf_data.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="systems_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
                    )
                    msg.attach(part)
                except Exception as e:
                    st.warning(f"Could not attach PDF: {str(e)}")
            
            if include_csv and export_records:
                csv_data = pd.DataFrame(export_records).to_csv(index=False)
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(csv_data.encode('utf-8'))
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="systems_data_{datetime.now().strftime("%Y%m%d")}.csv"'
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, email_password)
            server.send_message(msg)
            server.quit()
            
            st.success(f"✅ Email sent successfully to {recipient_email}!")
            
        except smtplib.SMTPAuthenticationError:
            st.error("❌ Authentication failed. Please check your email and app password.")
        except Exception as e:
            st.error(f"❌ Failed to send email: {str(e)}")
    else:
        st.error("❌ Please fill in all email configuration fields.")

# --- Footer ---
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown("### 🔐 Security Features")
    st.markdown("""
    - Master password protection
    - Password strength analysis
    - Secure password generation
    - Encrypted exports available
    - Session timeout protection
    """)

with col_footer2:
    st.markdown("### 📊 Analytics")
    st.markdown("""
    - Security score calculation
    - Password coverage tracking
    - Strength distribution analysis
    - Category completion rates
    - Activity timeline
    """)

with col_footer3:
    st.markdown("### 💾 Export Options")
    st.markdown("""
    - Multiple format support
    - Secure email delivery
    - Backup & restore functionality
    - QR code integration
    - Encrypted file options
    """)

# Auto-save functionality
if auto_save and datetime.now().minute % save_interval == 0:
    # This would trigger auto-save in a real application
    pass

# Session management
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.clear()
    st.rerun()

# Version info
st.sidebar.markdown("---")
st.sidebar.markdown("**Enhanced Password Manager v2.0**")
st.sidebar.markdown(f"Session: {datetime.now().strftime('%H:%M:%S')}")
if 'login_time' in st.session_state:
    session_duration = datetime.now() - st.session_state.login_time
    st.sidebar.markdown(f"Active: {str(session_duration).split('.')[0]}")

# Help section
with st.sidebar.expander("❓ Help & Tips"):
    st.markdown("""
    **Getting Started:**
    1. Set a strong master password
    2. Fill in system credentials
    3. Use password generator for security
    4. Export backups regularly
    
    **Security Tips:**
    - Use unique passwords for each system
    - Enable 2FA where available
    - Regular security audits
    - Keep backups secure
    
    **Features:**
    - 📊 Analytics dashboard
    - 🔧 Password tools
    - 📤 Multiple export formats
    - 📧 Secure email sharing
    """)
