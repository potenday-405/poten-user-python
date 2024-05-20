from passlib.context import CryptContext

# 비밀번호 암호화 및 검증을 위한 클래스
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password):
    """비밀번호 hash화"""
    return pwd_context.hash(password)