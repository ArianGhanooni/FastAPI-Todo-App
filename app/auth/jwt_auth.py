import datetime
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from user.models import TokenModel, UserModel
from core.database import get_db
from core.config import Settings
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError

security = HTTPBearer()
settings = Settings()


def get_authenticated_jwt_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials

    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id", None)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")
        if decoded.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed, Token Type is Not Valid")
        if  datetime.now() > datetime.fromtimestamp(decoded.get("exp")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed, Token Expired")

        user_obj = db.query(UserModel).filter_by(id = user_id).one()
        return user_obj

    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed, Invalid Signature Error")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed, Decode Error")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed, Expired Signature Error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication Failed, {e}")


def generate_access_token(user_id: int, expires_in: int = 3600):
    now = datetime.utcnow()

    payload = {
        "type": "access",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in)
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )

def refresh_access_token(user_id: int, expires_in: int = 3600):
    now = datetime.utcnow()

    payload = {
        "type": "refresh",
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in)
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )


def  decode_refresh_token(token):
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id", None)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials")
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed, Token Type is Not Valid")
        if  datetime.now() > datetime.fromtimestamp(decoded.get("exp")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed, Token Expired")

        return user_id

    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed, Invalid Signature Error")
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed, Decode Error")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed, Expired Signature Error")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication Failed, {e}")