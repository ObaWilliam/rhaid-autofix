import FastAPI, HTTPException, Request from fastapi 
import BaseModel from pydantic 
import jwt, datetime, os
import stripe
import smtplib
import EmailMessage from email.message 
import validate_email, EmailNotValidError from email_validator 
import load_dotenv from dotenv 
load_dotenv()


# Stripe keys from .env or hardcoded for live
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# Load private key
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "private.pem")
with open(PRIVATE_KEY_PATH, "rb") as f:
    PRIVATE_KEY = f.read()

app = FastAPI()


class IssueRequest(BaseModel):
    email: str
    plan: str  # e.g., "pro", "team", "enterprise"
    entitlements: list[str] = []
    expires_in: int = 365  # days

@app.post("/v1/license/issue")
def issue_license(req: IssueRequest):
    payload = {
        "email": req.email,
        "plan": req.plan,
        "entitlements": req.entitlements,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=req.expires_in)
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    # Optionally send email if requested
    send_license_email(req.email, token)
    return {"license_key": token}


class VerifyRequest(BaseModel):
    license_key: str


# Load public key for verification
PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_PATH", "public.pem")
with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY = f.read()

@app.post("/v1/license/verify")
def verify_license(req: VerifyRequest):
    try:
        payload = jwt.decode(req.license_key, PUBLIC_KEY, algorithms=["RS256"])
        return {"valid": True, "payload": payload}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Helper: Send license key by email
def send_license_email(email, license_key):
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    if not SMTP_USER or not SMTP_PASS:
        return False
    try:
        valid = validate_email(email)
        msg = EmailMessage()
        msg["Subject"] = "Your Rhaid License Key"
        msg["From"] = SMTP_USER
        msg["To"] = email
        msg.set_content(f"Thank you for your purchase!\n\nYour license key:\n{license_key}\n\nPaste this into your Rhaid app or extension.")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# Stripe webhook: handle payment and issue license
@app.post("/v1/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print(f"Stripe webhook error: {e}")
        return {"status": "error", "detail": str(e)}

    # Only handle successful payment
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email")
        plan = session.get("metadata", {}).get("plan", "pro")
        entitlements = []
        expires_in = 365
        # Issue license
        payload = {
            "email": email,
            "plan": plan,
            "entitlements": entitlements,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=expires_in)
        }
        token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
        # Send email
        sent = send_license_email(email, token)
        # Optionally display on web page (return in webhook response)
        return {"license_key": token, "email_sent": sent}
    return {"status": "ignored"}
