from src.utils.password import get_password_hash, verify_password


def test_get_password_hash():
    """测试生成密码哈希值"""
    password = "testpassword"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # 确保每次生成的哈希值不同
    assert hash1 != hash2
    
    # 确保哈希值不是明文
    assert hash1 != password
    assert hash2 != password


def test_verify_password():
    """测试验证密码"""
    password = "testpassword"
    hashed_password = get_password_hash(password)
    
    # 确保正确的密码能通过验证
    assert verify_password(password, hashed_password) is True
    
    # 确保错误的密码不能通过验证
    assert verify_password("wrongpassword", hashed_password) is False
    assert verify_password("", hashed_password) is False
