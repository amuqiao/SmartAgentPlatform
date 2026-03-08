def main(data_body: dict) -> tuple:
    """
    完整流程：解析数据 -> 生成图表 -> 上传OBS
    返回格式：(是否成功, 文件URL)
    """
    import os
    import json
    import datetime
    from obs import ObsClient
    from pyecharts.charts import Line
    from pyecharts import options as opts
    from pyecharts.render import make_snapshot
    from snapshot_selenium import snapshot  
    
    test_data = {
        "status_code": 200,
        "body": "{\"code\":0,\"msg\":\"success\",\"data\":{\"records\":[{\"id\":\"GF231230094212000515\",\"powerNumber\":\"GF231230094212000515\",\"powerName\":\"冉德平\",\"powerMark\":\"P82342\",\"buildStatus\":1,\"capacity\":45.650,\"url\":null,\"trafficStatus\":0,\"todayWeatherDTO\":{\"textDay\":\"晴\",\"high\":31,\"low\":14,\"wcDay\":\"<3级\",\"wdDay\":\"静风\"},\"incidentNum\":0,\"pwList\":[{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 05:45:00\",\"nearDate\":1742939100000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 06:00:00\",\"nearDate\":1742940000000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 06:15:00\",\"nearDate\":1742940900000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 06:30:00\",\"nearDate\":1742941800000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 06:45:00\",\"nearDate\":1742942700000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 07:00:00\",\"nearDate\":1742943600000,\"nearTimePW\":0.063},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 07:15:00\",\"nearDate\":1742944500000,\"nearTimePW\":0.419},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 07:30:00\",\"nearDate\":1742945400000,\"nearTimePW\":0.866},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 07:45:00\",\"nearDate\":1742946300000,\"nearTimePW\":1.326},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 08:00:00\",\"nearDate\":1742947200000,\"nearTimePW\":1.783},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 08:15:00\",\"nearDate\":1742948100000,\"nearTimePW\":2.216},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 08:30:00\",\"nearDate\":1742949000000,\"nearTimePW\":2.677},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 08:45:00\",\"nearDate\":1742949900000,\"nearTimePW\":3.252},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 09:00:00\",\"nearDate\":1742950800000,\"nearTimePW\":3.827},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 09:15:00\",\"nearDate\":1742951700000,\"nearTimePW\":4.213},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 09:30:00\",\"nearDate\":1742952600000,\"nearTimePW\":6.036},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 09:45:00\",\"nearDate\":1742953500000,\"nearTimePW\":8.047}],\"realTimePw\":10.570,\"dailyPower\":9.800,\"area\":\"四川省泸州市龙马潭区\",\"pr\":56.5400,\"powerFaultMarkList\":[],\"address\":\"来龙社区四组42号\",\"vendorName\":\"爱士惟\"}],\"total\":1},\"success\":true}",
        "headers": {
            "date": "Wed, 26 Mar 2025 01:55:01 GMT",
            "content-type": "application/json",
            "transfer-encoding": "chunked",
            "connection": "keep-alive",
            "set-cookie": "HWWAFSESID=ef1be7375994f33458; path=/, HWWAFSESTIME=1742954098714; path=/",
            "lubanops-gtrace-id": "v-649420-1742954098693-179028",
            "lubanops-nenv-id": "695182",
            "vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
            "access-control-allow-origin": "https://xuntian-pv.tcl.com",
            "access-control-expose-headers": "token",
            "access-control-allow-credentials": "true",
            "x-kong-upstream-latency": "2727",
            "x-kong-proxy-latency": "1",
            "via": "kong/1.4.0",
            "server": "CW",
            "content-encoding": "gzip"
        },
        "files": []
    }

    # 执行测试
    data_body = json.loads(test_data["body"])
    # print(f"{result}")
    
    # OBS配置（实际使用应从安全位置获取）
    obs_config = {
        'bucket_name': 'xuntian-cloud-prod',
        'ak': 'JFJHTI1HG05G6JVVAENR',
        'sk': 'KiVhfOfvBNXCKEvgq2JcbvSKyrW3wmIpuq5DoMwU',
        'endpoint': 'obs.cn-south-1.myhuaweicloud.com'
    }
    
    # 解析发电量数据
    def extract_pw_list_from_data(body_data: dict) -> dict:
        pw_list = body_data["data"]["records"][0]["pwList"]
        source_data = [["时间", "发电量(kW)"]]  # 带单位的标题行
        for item in pw_list:
            if item["nearTimePW"] > 0:
                time_str = item["nearTime"].split(" ")[1][:5]  # 格式化为"HH:MM"
                source_data.append([time_str, round(item["nearTimePW"], 3)])
        return {"source_data": source_data}

    # 生成ECharts配置
    def draw(source_data) -> dict:
        dimensions = source_data[0]
        x_data = [row[0] for row in source_data[1:]]
        y_data = [row[1] for row in source_data[1:]]

        return {
            "xAxis": x_data,
            "yAxis": y_data,
            "title": f"光伏电站{source_data[0][1]}趋势图",
            "subtitle": f"数据时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }

    def generate_with_matplotlib(echarts_data: dict) -> bytes:
        """使用Matplotlib生成图片字节流（跨平台优化版）"""
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import platform
        import subprocess
        from io import BytesIO
        from datetime import datetime

        # 操作系统检测与字体配置
        system = platform.system()
        font_config = {
            'Darwin': {  # macOS
                'font_name': 'Arial Unicode MS',
                'install_cmd': 'brew install --cask font-arial-unicode-ms',
                'fallback_fonts': ['Heiti TC', 'Songti SC']
            },
            'Linux': {
                'font_name': 'Noto Sans CJK SC',
                'install_cmd': 'sudo apt-get install fonts-noto-cjk',
                'fallback_fonts': ['WenQuanYi Micro Hei', 'Droid Sans Fallback']
            }
        }

        # 设置默认字体并验证可用性
        current_font = font_config.get(system, {})
        available_fonts = []
        
        if current_font:
            # 尝试检测首选字体
            try:
                from matplotlib.font_manager import findfont, FontProperties
                fp = FontProperties(family=current_font['font_name'])
                findfont(fp)
                plt.rcParams['font.family'] = current_font['font_name']
            except:
                # 字体不存在时尝试安装
                try:
                    print(f"正在尝试安装字体：{current_font['install_cmd']}")
                    subprocess.run(current_font['install_cmd'], shell=True, check=True)
                    plt.rcParams['font.family'] = current_font['font_name']
                except:
                    print(f"自动安装失败，请手动执行：{current_font['install_cmd']}")
                    available_fonts = current_font['fallback_fonts']
        
        # 设置备用字体
        if not available_fonts:
            available_fonts = ['sans-serif']  # 最终回退到系统默认
        plt.rcParams['font.sans-serif'] = available_fonts
        plt.rcParams['axes.unicode_minus'] = False

        # 以下保持原有绘图逻辑不变...
        # ... existing code ...
        plt.figure(figsize=(3.75, 6.67), dpi=100)
        x = [datetime.strptime(t, "%H:%M") for t in echarts_data["xAxis"]]
        y = echarts_data["yAxis"]
        plt.plot(x, y, color='#5470c6', linewidth=2, marker='o', markersize=4)
        plt.title(f"{echarts_data['title']}\n{echarts_data['subtitle']}", fontsize=12, pad=20)
        plt.xlabel("时间", fontsize=10)
        plt.ylabel("发电量(kW)", fontsize=10)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 生成内存流
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        return buf.getvalue()
    
    def upload_to_obs(ak, sk, endpoint, bucket_name, obs_object_key,
                      local_file_path=None, file_content=None):
        """
        上传文件/字节流到华为OBS（支持两种模式）

        参数:
            ak (str): 华为云的Access Key ID
            sk (str): 华为云的Secret Access Key
            endpoint (str): OBS服务端点
            bucket_name (str): OBS桶名称
            obs_object_key (str): 上传到OBS后的对象键名
            local_file_path (str): [文件模式]本地文件路径
            file_content (bytes): [流模式]文件字节内容

        返回:
            tuple: (是否成功, 文件URL)
        """
        # 参数校验
        if not (local_file_path or file_content):
            print("必须提供文件路径或文件内容")
            return False, None

        try:
            obs_client = ObsClient(
                access_key_id=ak, secret_access_key=sk, server=endpoint)

            # 文件模式处理
            if local_file_path:
                if not os.path.exists(local_file_path):
                    print(f"文件不存在: {local_file_path}")
                    return False, None
                with open(local_file_path, 'rb') as f:
                    content = f.read()
            # 流模式处理
            else:
                content = file_content

            resp = obs_client.putContent(
                bucketName=bucket_name,
                objectKey=obs_object_key,
                content=content
            )

            if resp.status < 300:
                file_url = f"https://xuntian-prod-obs.tclpv.com/{obs_object_key}"
                return True, file_url
            print(f"上传失败，状态码: {resp.status}")
            return False, None

        except Exception as e:
            print(f"上传异常: {str(e)}")
            return False, None
        finally:
            if 'obs_client' in locals():
                obs_client.close()

    try:
        
        success = False
        url = ""
        # 解析数据
        source_data = extract_pw_list_from_data(data_body)["source_data"]

        # 生成图表配置
        echarts_data = draw(source_data)

        # 生成内存字节流 上传到obs
        # image_bytes = generate_echarts_bytes(echarts_data)
        # if not image_bytes:
        #     return False, "图表生成失败"
        
        file_content = generate_with_matplotlib(echarts_data)
        

        # 构造OBS路径
        now = datetime.datetime.now()
        obs_key = f"7/images/wecome/{now.year}/{now.month}/{now.strftime('%Y%m%d%H%M%S')}.png"

        # 上传到OBS
        success, url = upload_to_obs(
            ak=obs_config['ak'],
            sk=obs_config['sk'],
            endpoint=obs_config['endpoint'],
            bucket_name=obs_config['bucket_name'],
            obs_object_key=obs_key,
            file_content=file_content
        )

        return {
            "success": "1" if success else "-1",
            "result": str(url)
        }


    except Exception as e:
        return {
            "success": "1" if success else "-1",
            "result": str(url)
        }


# 测试用例
if __name__ == "__main__":
    import json
    import time
    start = time.time()

    # 测试数据（来自download_echarts_image.py）
    test_data = {
        "body": '''{"data":{"records":[{"pwList":[
            {"nearTimePW":1.2, "nearTime":"2025-03-26 08:00:00"},
            {"nearTimePW":2.5, "nearTime":"2025-03-26 09:00:00"}
        ]}]}}'''
    }

    test_data = {
        "status_code": 200,
        "body": "{\"code\":0,\"msg\":\"success\",\"data\":{\"records\":[{\"id\":\"GF231230094212000515\",\"powerNumber\":\"GF231230094212000515\",\"powerName\":\"冉德平\",\"powerMark\":\"P82342\",\"buildStatus\":1,\"capacity\":45.650,\"url\":null,\"trafficStatus\":0,\"todayWeatherDTO\":{\"textDay\":\"晴\",\"high\":31,\"low\":14,\"wcDay\":\"<3级\",\"wdDay\":\"静风\"},\"incidentNum\":0,\"pwList\":[{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 05:45:00\",\"nearDate\":1742939100000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 06:00:00\",\"nearDate\":1742940000000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 06:15:00\",\"nearDate\":1742940900000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 06:30:00\",\"nearDate\":1742941800000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 06:45:00\",\"nearDate\":1742942700000,\"nearTimePW\":0.000},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 07:00:00\",\"nearDate\":1742943600000,\"nearTimePW\":0.063},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 07:15:00\",\"nearDate\":1742944500000,\"nearTimePW\":0.419},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 07:30:00\",\"nearDate\":1742945400000,\"nearTimePW\":0.866},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 07:45:00\",\"nearDate\":1742946300000,\"nearTimePW\":1.326},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 08:00:00\",\"nearDate\":1742947200000,\"nearTimePW\":1.783},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 08:15:00\",\"nearDate\":1742948100000,\"nearTimePW\":2.216},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 08:30:00\",\"nearDate\":1742949000000,\"nearTimePW\":2.677},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 08:45:00\",\"nearDate\":1742949900000,\"nearTimePW\":3.252},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 09:00:00\",\"nearDate\":1742950800000,\"nearTimePW\":3.827},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 09:15:00\",\"nearDate\":1742951700000,\"nearTimePW\":4.213},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 09:30:00\",\"nearDate\":1742952600000,\"nearTimePW\":6.036},{\"powerStationId\":\"P82342\",\"nearTime\":\"2025-03-26 09:45:00\",\"nearDate\":1742953500000,\"nearTimePW\":8.047}],\"realTimePw\":10.570,\"dailyPower\":9.800,\"area\":\"四川省泸州市龙马潭区\",\"pr\":56.5400,\"powerFaultMarkList\":[],\"address\":\"来龙社区四组42号\",\"vendorName\":\"爱士惟\"}],\"total\":1},\"success\":true}",
        "headers": {
            "date": "Wed, 26 Mar 2025 01:55:01 GMT",
            "content-type": "application/json",
            "transfer-encoding": "chunked",
            "connection": "keep-alive",
            "set-cookie": "HWWAFSESID=ef1be7375994f33458; path=/, HWWAFSESTIME=1742954098714; path=/",
            "lubanops-gtrace-id": "v-649420-1742954098693-179028",
            "lubanops-nenv-id": "695182",
            "vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
            "access-control-allow-origin": "https://xuntian-pv.tcl.com",
            "access-control-expose-headers": "token",
            "access-control-allow-credentials": "true",
            "x-kong-upstream-latency": "2727",
            "x-kong-proxy-latency": "1",
            "via": "kong/1.4.0",
            "server": "CW",
            "content-encoding": "gzip"
        },
        "files": []
    }

    # 执行测试
    result = main(
        json.loads(test_data["body"]))
    
    end = time.time()
    print(f"总执行时间: {end - start:.2f}秒")
    print(f"{result}")
