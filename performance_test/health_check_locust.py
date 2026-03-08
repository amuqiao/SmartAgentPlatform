from locust import HttpUser, task, between


class HealthCheckUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_liveness_check(self):
        self.client.get("/api/v1/health/liveness")

    @task
    def test_readiness_check(self):
        self.client.get("/api/v1/health/readiness")

    @task(3)
    def test_mixed_health_checks(self):
        self.client.get("/api/v1/health/liveness")
        self.client.get("/api/v1/health/readiness")


# 运行说明：
# 1. 确保FastAPI服务正在运行（默认端口8000）
# 2. 在项目根目录执行以下命令：
#    uv run locust -f performance_test/health_check_locust.py --host http://localhost:8000 --web-port 8089
# 3. 访问 http://localhost:8089 即可使用Web UI进行压测
# 4. 设置并发用户数和孵化率，点击"Start swarming"开始压测
# 5. 可以在Web UI中实时查看压测结果和性能指标

# 当前状态：
# ✓ Locust服务已成功启动，运行在 http://localhost:8089
# ✓ 已解决TOML文件编码问题
# ✓ 可以正常使用Web UI进行压测

# 问题修复说明：
# - 原问题：Locust解析pyproject.toml时遇到GBK编码错误
# - 解决方案：移除了pyproject.toml中的所有中文字符和中文注释
# - 结果：Locust可以正常启动和运行
