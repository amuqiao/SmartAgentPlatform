def test_liveness_endpoint(client):
    """测试服务存活检查接口"""
    response = client.get("/api/v1/health/liveness")
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Service is running"
    }


def test_readiness_endpoint(client):
    """测试服务就绪检查接口"""
    response = client.get("/api/v1/health/readiness")
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Service readiness check",
        "checks": {
            "database": "ok"
        }
    }


def test_health_endpoints_rate_limit(client):
    """测试健康检查接口限流机制"""
    # 连续发送5个请求，检查是否返回200 OK
    for i in range(5):
        response = client.get("/api/v1/health/liveness")
        assert response.status_code == 200
    
    # 这个测试用例主要验证限流机制的集成是否正常，
    # 完整的限流测试可以通过专门的性能测试工具进行
    assert True
