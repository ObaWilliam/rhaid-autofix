# Rhaid License Verification (Offline)
import jwt

PUBLIC_KEY_PATH = "public.pem"

def resolve_license(license_key: str) -> dict:
    """Verify JWT license offline using public.pem."""
    try:
        with open(PUBLIC_KEY_PATH, "rb") as f:
            public_key = f.read()
        payload = jwt.decode(license_key, public_key, algorithms=["RS256"])
        return payload
    except Exception as e:
        return {"error": str(e)}

def has(entitlements, feature: str) -> bool:
    """Check if feature is in entitlements list."""
    return feature in entitlements if entitlements else False
