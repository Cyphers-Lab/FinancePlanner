"""Authentication service for the Financial Planner application."""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session
from ..models.models import User

class AuthService:
    """Service for handling user authentication and security."""

    def __init__(self):
        """Initialize the authentication service."""
        # Get secret key from environment or generate random bytes
        secret_key = os.getenv("SECRET_KEY")
        if secret_key is None:
            self.secret_key = os.urandom(32)
        else:
            self.secret_key = secret_key.encode('utf-8')
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption components."""
        # Get salt from environment or generate random bytes
        salt = os.getenv("ENCRYPTION_SALT")
        if salt is None:
            salt = os.urandom(16)
        else:
            salt = salt.encode('utf-8')

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key))
        self.cipher_suite = Fernet(key)

    def hash_password(self, password: str) -> str:
        """Hash a password for storing."""
        return self.cipher_suite.encrypt(password.encode()).decode()

    def verify_password(self, stored_hash: str, provided_password: str) -> bool:
        """Verify a stored password against a provided password."""
        try:
            decrypted = self.cipher_suite.decrypt(stored_hash.encode()).decode()
            return decrypted == provided_password
        except Exception:
            return False

    def create_user(
        self, 
        db: Session, 
        username: str, 
        email: str, 
        password: str,
        currency: str = '$'
    ) -> User:
        """Create a new user with encrypted password."""
        password_hash = self.hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            currency=currency,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_user_currency(self, db: Session, user_id: int, currency: str) -> User:
        """Update a user's preferred currency."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.currency = currency
            db.commit()
            db.refresh(user)
        return user

    def authenticate_user(self, db: Session, username: str, password: str) -> User:
        """Authenticate a user and return user object if successful."""
        user = db.query(User).filter(User.username == username).first()
        if user and self.verify_password(user.password_hash, password):
            return user
        return None

    def create_access_token(self, user_id: int, expires_delta: timedelta = None) -> str:
        """Create a JWT access token for the user."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=15)
            
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "exp": expire,
            "user_id": user_id
        }
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> dict:
        """Verify a JWT token and return payload if valid."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def get_current_user(self, db: Session, token: str) -> User:
        """Get current user from database using token."""
        payload = self.verify_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise ValueError("Invalid token payload")
            
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise ValueError("User not found")
            
        return user
