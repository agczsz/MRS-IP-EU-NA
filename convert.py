import re
import requests
import subprocess
import os

# --- 配置 ---
REPO_API_URL = "https://api.github.com/repos/Hamster-Prime/Bird_Global_List/contents/Country_CIDR"
RAW_BASE_URL = "https://github.com/Hamster-Prime/Bird_Global_List/raw/main/Country_CIDR/"
MIHOMO_PATH = "./mihomo"
BASE_DIR = "Continents"

# 大洲国家代码映射
CONTINENT_MAP = {
    "EU": ["GR", "EE", "LV", "LT", "SJ", "MD", "BY", "FI", "AX", "UA", "MK", "HU", "BG", "AL", "PL", "RO", "XK", "RU", "PT", "GI", "ES", "MT", "FO", "DK", "IS", "GB", "CH", "SE", "NL", "AT", "BE", "DE", "LU", "IE", "MC", "FR", "AD", "LI", "JE", "IM", "GG", "SK", "CZ", "NO", "VA", "SM", "IT", "SI", "ME", "HR", "BA", "RS"],
    "NA": ["US", "CA"]
}

def fetch_cidrs(url):
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return re.findall(r'route\s+([\d\./]+)\s+via', resp.text)
    except Exception as e:
        print(f"[!] 下载失败 {url}: {e}")
        return []

def convert_to_mrs(cidr_list, output_path):
    if not cidr_list:
        return
    
    # 写入临时 YAML
    temp_yaml = "temp.yaml"
    # 使用 set 去重
    unique_cidrs = sorted(list(set(cidr_list)))
    
    with open(temp_yaml, "w") as f:
        f.write("payload:\n")
        for cidr in unique_cidrs:
            f.write(f"  - '{cidr}'\n")
    
    # 执行转换
    # 注意：确保 output_path 的父目录已存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cmd = [MIHOMO_PATH, "convert-ruleset", "ipcidr", "yaml", temp_yaml, output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[!] 转换失败 {output_path}: {result.stderr}")
    else:
        print(f"[#] 成功: {output_path} (条目数: {len(unique_cidrs)})")
    
    if os.path.exists(temp_yaml):
        os.remove(temp_yaml)

def main():
    print("[*] 正在获取文件列表...")
    resp = requests.get(REPO_API_URL)
    resp.raise_for_status()
    conf_files = [item['name'] for item in resp.json() if item['name'].endswith('.conf')]

    # 用于存放各洲合并的原始 CIDR 列表
    continent_data = {key: [] for key in CONTINENT_MAP.keys()}

    for filename in conf_files:
        cc = filename.replace(".conf", "")
        url = RAW_BASE_URL + filename
        cidrs = fetch_cidrs(url)
        
        if not cidrs: continue

        # 查找该国家属于哪个洲
        target_continent = None
        for cont, codes in CONTINENT_MAP.items():
            if cc in codes:
                target_continent = cont
                break
        
        # 1. 生成单个国家文件，存放在 Continents/洲名/国家.mrs
        if target_continent:
            save_path = os.path.join(BASE_DIR, target_continent, f"{cc}.mrs")
            continent_data[target_continent].extend(cidrs) # 存入合并列表
        else:
            # 如果不在 EU/NA 列表中，放入 Other 文件夹
            save_path = os.path.join(BASE_DIR, "Other", f"{cc}.mrs")
        
        convert_to_mrs(cidrs, save_path)

    # 2. 生成大洲合并文件，存放在 Continents/洲名.mrs
    print("\n[*] 正在生成大洲合并规则...")
    for cont, all_cidrs in continent_data.items():
        if all_cidrs:
            cont_output = os.path.join(BASE_DIR, f"{cont}.mrs")
            print(f"[*] 正在合并 {cont}，原始总条数: {len(all_cidrs)}")
            convert_to_mrs(all_cidrs, cont_output)

if __name__ == "__main__":
    main()
