import os
import pandas as pd
import subprocess
import requests
import shutil

# --- 配置 ---
TOKEN = os.getenv("IPINFO_TOKEN")
DB_URL = f"https://ipinfo.io/data/ipinfo_lite.csv.gz?token={TOKEN}"
CSV_FILE = "ipinfo_lite.csv.gz"
MIHOMO_PATH = "./mihomo"
OUTPUT_DIR = "Continents"

# 大洲映射
CONTINENT_MAP = {
    "EU": ["GR", "EE", "LV", "LT", "SJ", "MD", "BY", "FI", "AX", "UA", "MK", "HU", "BG", "AL", "PL", "RO", "XK", "RU", "PT", "GI", "ES", "MT", "FO", "DK", "IS", "GB", "CH", "SE", "NL", "AT", "BE", "DE", "LU", "IE", "MC", "FR", "AD", "LI", "JE", "IM", "GG", "SK", "CZ", "NO", "VA", "SM", "IT", "SI", "ME", "HR", "BA", "RS"],
    "NA": ["US", "CA", "MX", "GL", "CU", "PR"]
}

def download_database():
    print(f"[*] 正在下载 ipinfo 数据库...")
    response = requests.get(DB_URL, stream=True)
    if response.status_code == 200:
        with open(CSV_FILE, 'wb') as f:
            f.write(response.raw.read())
        print("[+] 下载完成")
    else:
        raise Exception(f"下载失败，状态码: {response.status_code}")

def convert_to_mrs(cidr_list, output_path):
    if not cidr_list:
        return
    
    # 转换前去重并排序
    unique_cidrs = sorted(list(set(cidr_list)))
    temp_yaml = "temp.yaml"
    
    with open(temp_yaml, "w") as f:
        f.write("payload:\n")
        for cidr in unique_cidrs:
            # 确保 CIDR 格式正确
            if '/' not in str(cidr):
                cidr = f"{cidr}/128" if ':' in str(cidr) else f"{cidr}/32"
            f.write(f"  - '{cidr}'\n")
    
    # 调用 mihomo 转换
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [MIHOMO_PATH, "convert-ruleset", "ipcidr", "yaml", temp_yaml, output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[!] 转换失败: {result.stderr}")
    
    if os.path.exists(temp_yaml):
        os.remove(temp_yaml)

def main():
    if not TOKEN:
        print("[!] 错误: 未设置 IPINFO_TOKEN 环境变量")
        return

    # 1. 下载
    download_database()

    # 2. 读取数据 (pandas 可以直接读取 .gz)
    print("[*] 正在加载数据并处理...")
    df = pd.read_csv(CSV_FILE, compression='gzip')

    # 准备大洲统计
    continent_data = {key: [] for key in CONTINENT_MAP.keys()}
    continent_data["Other"] = []

    # 3. 按国家分组处理
    print("[*] 开始生成各国家 MRS 文件...")
    for cc, group in df.groupby('country_code'):
        cidrs = group['network'].tolist()
        
        # 确定归属大洲
        target_cont = "Other"
        for cont, codes in CONTINENT_MAP.items():
            if cc in codes:
                target_cont = cont
                break
        
        # 生成国家 MRS
        country_path = os.path.join(OUTPUT_DIR, target_cont, f"{cc}.mrs")
        convert_to_mrs(cidrs, country_path)
        
        # 汇总到大洲
        continent_data[target_cont].extend(cidrs)

    # 4. 生成大洲合并 MRS
    print("\n[*] 正在生成大洲合并 MRS 文件...")
    for cont, all_cidrs in continent_data.items():
        if all_cidrs:
            cont_path = os.path.join(OUTPUT_DIR, f"{cont}.mrs")
            print(f"[*] 处理大洲: {cont} (条目数: {len(all_cidrs)})")
            convert_to_mrs(all_cidrs, cont_path)

    print("\n[V] 任务全部完成！")

if __name__ == "__main__":
    main()
