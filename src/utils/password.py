import bcrypt


def get_password_hash(password: str) -> str:
    """生成密码哈希值"""
    # 将密码转换为字节串
    password_bytes = password.encode('utf-8')
    # 生成salt
    salt = bcrypt.gensalt()
    # 生成哈希值
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # 将哈希值转换为字符串并返回
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # 将密码和哈希值转换为字节串
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    # 验证密码
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
