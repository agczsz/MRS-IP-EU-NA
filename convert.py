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

# 大洲映射 (可根据需要扩展)
CONTINENT_MAP = {
    "EU": ["GR", "EE", "LV", "LT", "SJ", "MD", "BY", "FI", "AX", "UA", "MK", "HU", "BG", "AL", "PL", "RO", "XK", "RU", "PT", "GI", "ES", "MT", "FO", "DK", "IS", "GB", "CH", "SE", "NL", "AT", "BE", "DE", "LU", "IE", "MC", "FR", "AD", "LI", "JE", "IM", "GG", "SK", "CZ", "NO", "VA", "SM", "IT", "SI", "ME", "HR", "BA", "RS"],
    "NA": ["US", "CA", "MX", "GL", "CU", "PR"],
    "AS": ["CN", "JP", "KR", "HK", "TW", "SG", "MY", "TH", "VN", "ID", "IN", "PH"],
    "OC": ["AU", "NZ"],
    "SA": ["BR", "AR", "CL", "CO"],
    "AF": ["ZA", "EG", "NG"]
}

def download_database():
    print(f"[*] 正在从 ipinfo 下载数据库...")
    response = requests.get(DB_URL, stream=True)
    if response.status_code == 200:
        with open(CSV_FILE, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("[+] 下载完成")
    else:
        raise Exception(f"下载失败，状态码: {response.status_code}. 请检查 Token 是否有效。")

def convert_to_mrs(cidr_list, output_path):
    if not cidr_list:
        return
    
    # 彻底确保只处理 IPv4 且去重排序
    unique_cidrs = sorted(list(set([c for c in cidr_list if ':' not in str(c)])))
    if not unique_cidrs:
        return

    temp_yaml = f"temp_{os.path.basename(output_path)}.yaml"
    
    with open(temp_yaml, "w") as f:
        f.write("payload:\n")
        for cidr in unique_cidrs:
            if '/' not in str(cidr):
                cidr = f"{cidr}/32"
            f.write(f"  - '{cidr}'\n")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [MIHOMO_PATH, "convert-ruleset", "ipcidr", "yaml", temp_yaml, output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[!] 转换失败 {output_path}: {result.stderr}")
    
    if os.path.exists(temp_yaml):
        os.remove(temp_yaml)

def main():
    if not TOKEN:
        print("[!] 错误: 未检测到环境变量 IPINFO_TOKEN")
        return

    # 1. 下载数据库
    download_database()

    # 2. 读取并过滤数据
    print("[*] 正在加载数据并剔除 IPv6...")
    df = pd.read_csv(CSV_FILE, compression='gzip')
    
    # 【关键修改】只保留不含冒号的行 (即剔除 IPv6)
    df = df[~df['network'].str.contains(':')].copy()
    print(f"[+] 过滤完成，剩余 IPv4 条目: {len(df)}")

    # 准备容器
    continent_data = {key: [] for key in CONTINENT_MAP.keys()}
    continent_data["Other"] = []

    # 3. 按国家分组生成单文件
    print("[*] 开始生成各国家/地区 IPv4 MRS 文件...")
    for cc, group in df.groupby('country_code'):
        cidrs = group['network'].tolist()
        
        target_cont = "Other"
        for cont, codes in CONTINENT_MAP.items():
            if cc in codes:
                target_cont = cont
                break
        
        country_path = os.path.join(OUTPUT_DIR, target_cont, f"{cc}.mrs")
        convert_to_mrs(cidrs, country_path)
        
        # 汇总给大洲
        continent_data[target_cont].extend(cidrs)

    # 4. 生成大洲合并文件
    print("\n[*] 正在生成大洲合并 IPv4 MRS...")
    for cont, all_cidrs in continent_data.items():
        if all_cidrs:
            cont_path = os.path.join(OUTPUT_DIR, f"{cont}.mrs")
            print(f"[*] 处理大洲: {cont} (条目: {len(set(all_cidrs))})")
            convert_to_mrs(all_cidrs, cont_path)

    print("\n[V] 任务全部完成！")

if __name__ == "__main__":
    main()
