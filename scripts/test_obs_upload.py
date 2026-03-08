#!/usr/bin/env python3
"""
测试上传txt文件到华为OBS
支持两种上传模式：
1. 文件模式：从本地文件上传
2. 流模式：直接上传内存中的字节内容

安装前置条件：
pip install esdk-obs-python --trusted-host mirrors.huaweicloud.com -i https://mirrors.huaweicloud.com/repository/pypi/simple
"""

import os
import json
import time
import logging
import datetime
from typing import Dict, Tuple, Optional, Any, Union
from obs import ObsClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 常量定义
OBS_URL_PREFIX = "https://xuntian-prod-obs.tclpv.com"
TEST_BUCKET_NAME = "xuntian-cloud-prod"
TEST_ENDPOINT = "obs.cn-south-1.myhuaweicloud.com"

# OBS配置（实际使用应从环境变量或配置文件获取）
OBS_CONFIG = {
    'bucket_name': TEST_BUCKET_NAME,
    'ak': 'JFJHTI1HG05G6JVVAENR',
    'sk': 'KiVhfOfvBNXCKEvgq2JcbvSKyrW3wmIpuq5DoMwU',
    'endpoint': TEST_ENDPOINT
}


class ObsUploader:
    """OBS上传器类，封装OBS上传功能"""
    
    def __init__(self, ak: str, sk: str, endpoint: str, bucket_name: str):
        """
        初始化OBS上传器
        
        Args:
            ak: 华为云的Access Key ID
            sk: 华为云的Secret Access Key
            endpoint: OBS服务端点
            bucket_name: OBS桶名称
        """
        self.ak = ak
        self.sk = sk
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.obs_client: Optional[ObsClient] = None
    
    def __enter__(self) -> 'ObsUploader':
        """进入上下文管理器，创建OBS客户端"""
        try:
            self.obs_client = ObsClient(
                access_key_id=self.ak, 
                secret_access_key=self.sk, 
                server=self.endpoint
            )
            logger.info("OBS客户端创建成功")
        except Exception as e:
            logger.error(f"创建OBS客户端失败: {str(e)}")
            raise
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器，关闭OBS客户端"""
        if self.obs_client:
            try:
                self.obs_client.close()
                logger.info("OBS客户端关闭成功")
            except Exception as e:
                logger.error(f"关闭OBS客户端失败: {str(e)}")
    
    def upload_file(self, local_file_path: str, obs_object_key: str) -> Tuple[bool, str, Optional[str]]:
        """
        从本地文件上传到OBS
        
        Args:
            local_file_path: 本地文件路径
            obs_object_key: 上传到OBS后的对象键名
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 文件URL, 错误信息)
        """
        if not os.path.exists(local_file_path):
            error_msg = f"文件不存在: {local_file_path}"
            logger.error(error_msg)
            return False, "", error_msg
        
        try:
            with open(local_file_path, 'rb') as f:
                content = f.read()
            return self.upload_content(content, obs_object_key)
        except Exception as e:
            error_msg = f"读取本地文件失败: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def upload_content(self, file_content: bytes, obs_object_key: str) -> Tuple[bool, str, Optional[str]]:
        """
        直接上传字节内容到OBS（流模式）
        
        Args:
            file_content: 文件字节内容
            obs_object_key: 上传到OBS后的对象键名
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 文件URL, 错误信息)
        """
        if not self.obs_client:
            error_msg = "OBS客户端未初始化"
            logger.error(error_msg)
            return False, "", error_msg
        
        try:
            resp = self.obs_client.putContent(
                bucketName=self.bucket_name,
                objectKey=obs_object_key,
                content=file_content
            )
            
            if resp.status < 300:
                file_url = f"{OBS_URL_PREFIX}/{obs_object_key}"
                logger.info(f"上传成功! 文件URL: {file_url}")
                return True, file_url, None
            else:
                error_msg = f"上传失败，状态码: {resp.status}, 错误信息: {resp.body.get('Message', '未知错误')}"
                logger.error(error_msg)
                return False, "", error_msg
        except Exception as e:
            error_msg = f"上传异常: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg


def generate_obs_key(prefix: str) -> str:
    """
    生成OBS对象键
    
    Args:
        prefix: OBS键前缀
        
    Returns:
        str: 完整的OBS对象键
    """
    now = datetime.datetime.now()
    return f"7/test/{prefix}/{now.year}/{now.month}/{now.strftime('%Y%m%d%H%M%S')}.txt"


def create_test_file(content: str, file_path: str) -> None:
    """
    创建测试文件
    
    Args:
        content: 测试文件内容
        file_path: 测试文件路径
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"已创建测试文件: {file_path}")
    logger.debug(f"文件内容:\n{content}")


def cleanup_test_file(file_path: str) -> None:
    """
    清理测试文件
    
    Args:
        file_path: 测试文件路径
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"已清理测试文件: {file_path}")


def test_upload_txt_file(uploader: ObsUploader) -> Dict[str, Any]:
    """
    测试从本地文件上传txt到OBS
    
    Args:
        uploader: OBS上传器实例
        
    Returns:
        Dict: 测试结果
    """
    logger.info("\n=== 测试1: 从本地文件上传txt到OBS ===")
    
    # 创建测试txt文件
    test_txt_content = "这是一个测试文件，用于测试从本地文件上传txt到OBS。\n测试内容第二行。\n测试内容第三行。"
    test_txt_path = "test_upload.txt"
    
    try:
        # 写入测试文件
        create_test_file(test_txt_content, test_txt_path)
        
        # 构造OBS路径
        obs_key = generate_obs_key("txt")
        
        # 上传到OBS
        success, url, error = uploader.upload_file(test_txt_path, obs_key)
        
        return {
            "test_name": "从本地文件上传",
            "success": success,
            "url": url,
            "error": error,
            "test_file": test_txt_path
        }
    finally:
        # 清理测试文件
        cleanup_test_file(test_txt_path)


def test_upload_txt_content(uploader: ObsUploader) -> Dict[str, Any]:
    """
    测试直接上传txt内容到OBS（流模式）
    
    Args:
        uploader: OBS上传器实例
        
    Returns:
        Dict: 测试结果
    """
    logger.info("\n=== 测试2: 直接上传txt内容到OBS（流模式） ===")
    
    # 测试txt内容
    test_txt_content = "这是一个直接上传内容的测试文件，用于测试流模式上传txt到OBS。\n测试内容第二行。\n测试内容第三行。"
    test_txt_bytes = test_txt_content.encode('utf-8')
    
    logger.info(f"准备上传的内容:\n{test_txt_content}")
    
    # 构造OBS路径
    obs_key = generate_obs_key("txt_content")
    
    # 上传到OBS（流模式）
    success, url, error = uploader.upload_content(test_txt_bytes, obs_key)
    
    return {
        "test_name": "直接上传内容（流模式）",
        "success": success,
        "url": url,
        "error": error,
        "test_mode": "stream_mode"
    }


def run_tests() -> Dict[str, Dict[str, Any]]:
    """
    运行所有测试
    
    Returns:
        Dict: 所有测试结果
    """
    logger.info("=== 开始测试OBS上传txt文件功能 ===")
    start_time = time.time()
    logger.info(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 使用上下文管理器管理OBS客户端
    with ObsUploader(
        ak=OBS_CONFIG['ak'],
        sk=OBS_CONFIG['sk'],
        endpoint=OBS_CONFIG['endpoint'],
        bucket_name=OBS_CONFIG['bucket_name']
    ) as uploader:
        
        # 运行测试
        results["test1"] = test_upload_txt_file(uploader)
        results["test2"] = test_upload_txt_content(uploader)
    
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info("\n=== 测试结果汇总 ===")
    logger.info(json.dumps(results, indent=2, ensure_ascii=False))
    
    # 统计成功率
    success_count = sum(1 for result in results.values() if result["success"])
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    logger.info("\n=== 测试完成 ===")
    logger.info(f"总测试数: {total_count}")
    logger.info(f"成功数: {success_count}")
    logger.info(f"成功率: {success_rate:.1f}%")
    logger.info(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"总耗时: {duration:.2f}秒")
    
    return results


def main():
    """
    主函数，运行所有测试
    """
    run_tests()


if __name__ == "__main__":
    main()
