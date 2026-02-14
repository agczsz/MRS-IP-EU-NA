import re
import requests
import subprocess
import os

# --- 配置 ---
SOURCE_URL = "https://github.com/bgptools/anycast-prefixes/raw/refs/heads/master/anycatch-v4-prefixes.txt"
MIHOMO_PATH = "./mihomo"
OUTPUT_PATH = "anycast/anycatch-v4-prefixes.mrs" # 直接指定到 anycast 目录

def fetch_cidrs(url):
    try:
        print(f"[*] 正在从 {url} 下载数据...")
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        # 匹配标准 CIDR 格式
        return re.findall(r'(\d{1,3}(?:\.\d{1,3}){3}/\d{1,2})', resp.text)
    except Exception as e:
        print(f"[!] 下载失败: {e}")
        return []

def convert_to_mrs(cidr_list, output_path):
    if not cidr_list:
        return

    temp_yaml = "temp_anycast.yaml"
    unique_cidrs = sorted(list(set(cidr_list)))

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(temp_yaml, "w") as f:
        f.write("payload:\n")
        for cidr in unique_cidrs:
            f.write(f"  - '{cidr}'\n")

    print(f"[*] 正在转换 {len(unique_cidrs)} 条 CIDR...")
    cmd = [MIHOMO_PATH, "convert-ruleset", "ipcidr", "yaml", temp_yaml, output_path]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] 转换失败: {result.stderr}")
    else:
        print(f"[#] 成功生成: {output_path}")

    if os.path.exists(temp_yaml):
        os.remove(temp_yaml)

if __name__ == "__main__":
    cidrs = fetch_cidrs(SOURCE_URL)
    if cidrs:
        convert_to_mrs(cidrs, OUTPUT_PATH)
