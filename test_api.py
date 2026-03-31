"""
测试API连接
"""
import requests

def test_api():
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("测试 API 连接")
    print("=" * 50)
    
    # 1. 健康检查
    print("\n[1] 健康检查...")
    try:
        resp = requests.get(f"{base_url}/api/v1/health", timeout=5)
        print(f"✅ 状态码: {resp.status_code}")
        print(f"   响应: {resp.json()}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        return
    
    # 2. 平台列表
    print("\n[2] 平台列表...")
    try:
        resp = requests.get(f"{base_url}/api/v1/platforms", timeout=5)
        print(f"✅ 状态码: {resp.status_code}")
        print(f"   平台: {resp.json()}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 3. B站搜索
    print("\n[3] B站搜索测试...")
    try:
        resp = requests.get(f"{base_url}/api/v1/search", 
                          params={
                              "keyword": "原神",
                              "platform": "bilibili",
                              "page": 1,
                              "page_size": 5
                          }, 
                          timeout=10)
        print(f"✅ 状态码: {resp.status_code}")
        data = resp.json()
        if data.get("success"):
            print(f"   找到视频: {len(data.get('data', {}).get('items', []))} 个")
        else:
            print(f"   错误: {data.get('message')}")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_api()
