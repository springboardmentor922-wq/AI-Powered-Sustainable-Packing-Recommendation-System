"""
Authentication Module
---------------------
- Email/password authentication
- Bcrypt password hashing
- 3-attempt lockout mechanism
- First-time password setup
"""

import logging
import bcrypt
import pymysql
from typing import Tuple, Dict

from db import get_db

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3


# ======================================================
# 🔐 Helpers
# ======================================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


# ======================================================
# 🧾 Registration
# ======================================================

def register_email(email: str) -> Tuple[Dict, int]:
    """
    Register email only.
    Password is set on first successful login.
    """
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, password_hash, failed_attempts, is_locked)
                VALUES (%s, NULL, 0, FALSE)
                """,
                (email,)
            )
        db.commit()
        logger.info(f"✅ Email registered: {email}")
        return {"success": True, "message": "Email registered"}, 201

    except pymysql.err.IntegrityError:
        logger.warning(f"⚠️ Email already exists: {email}")
        return {"error": "Email already exists"}, 409

    except Exception as e:
        logger.exception("Registration error")
        return {"error": "Registration failed"}, 500

    finally:
        db.close()


# ======================================================
# 🔑 Login
# ======================================================

"""
Authentication Module
- Email/password authentication
- Auto user creation on first login
- Bcrypt password hashing
- 3-attempt lockout mechanism
"""

import bcrypt
import logging
import pymysql
from db import get_db

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3


def login_user(email, password):
    """
    Unified login flow:
    - If email does not exist → create user + set password
    - If exists & no password → set password
    - If exists & password → verify
    """

    db = get_db()
    try:
        with db.cursor() as cur:
            # Fetch user
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

            # ==================================================
            # CASE 1: USER DOES NOT EXIST → AUTO REGISTER
            # ==================================================
            if not user:
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

                cur.execute(
                    """
                    INSERT INTO users (email, password_hash, failed_attempts, is_locked, last_login)
                    VALUES (%s, %s, 0, FALSE, NOW())
                    """,
                    (email, hashed.decode())
                )

                logger.info(f"🆕 Auto-registered new user: {email}")

                return {
                    "success": True,
                    "message": "Account created & logged in",
                    "email": email,
                    "first_login": True
                }, 200

            # ==================================================
            # CASE 2: ACCOUNT LOCKED
            # ==================================================
            if user["is_locked"]:
                logger.warning(f"🔒 Account locked: {email}")
                return {"error": "ACCESS DENIED", "locked": True}, 403

            # ==================================================
            # CASE 3: FIRST LOGIN (PASSWORD NOT SET)
            # ==================================================
            if user["password_hash"] is None:
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

                cur.execute(
                    """
                    UPDATE users
                    SET password_hash=%s, last_login=NOW()
                    WHERE email=%s
                    """,
                    (hashed.decode(), email)
                )

                logger.info(f"🔐 Password set for first-time user: {email}")

                return {
                    "success": True,
                    "message": "Password set & logged in",
                    "email": email,
                    "first_login": True
                }, 200

            # ==================================================
            # CASE 4: NORMAL LOGIN → VERIFY PASSWORD
            # ==================================================
            if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
                cur.execute(
                    """
                    UPDATE users
                    SET failed_attempts=0, last_login=NOW()
                    WHERE email=%s
                    """,
                    (email,)
                )

                logger.info(f"✅ Login successful: {email}")

                return {
                    "success": True,
                    "message": "Login successful",
                    "email": email
                }, 200

            # ==================================================
            # CASE 5: WRONG PASSWORD
            # ==================================================
            attempts = user["failed_attempts"] + 1
            locked = attempts >= MAX_ATTEMPTS

            cur.execute(
                """
                UPDATE users
                SET failed_attempts=%s, is_locked=%s
                WHERE email=%s
                """,
                (attempts, locked, email)
            )

            if locked:
                logger.warning(f"🔒 Account locked after {MAX_ATTEMPTS} attempts: {email}")
                return {"error": "ACCESS DENIED", "locked": True}, 403

            return {
                "error": "Invalid password",
                "attempts_remaining": MAX_ATTEMPTS - attempts
            }, 401

    except Exception as e:
        logger.exception("Authentication error")
        return {"error": "Authentication failed"}, 500

    finally:
        db.close()

# ======================================================
# 🔓 Admin Unlock
# ======================================================

def unlock_account(email: str) -> Tuple[Dict, int]:
    """Admin-only: unlock a locked account"""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET is_locked=FALSE, failed_attempts=0
                WHERE email=%s
                """,
                (email,)
            )
        db.commit()
        logger.info(f"🔓 Account unlocked: {email}")
        return {"success": True}, 200

    except Exception:
        logger.exception("Unlock error")
        return {"error": "Unlock failed"}, 500

    finally:
        db.close()

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    # Test
    print("Testing authentication...")
    result, status = login_user("test@ecopackai.com", "testpass123")
    print(f"Result: {result}, Status: {status}")