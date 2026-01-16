# MRS-IP-EU-NA

基于 **MRS（Meta Routing Set）格式** 的 **IPCIDR GeoIP 数据集**，按**洲 / 地区**拆分，适用于 Mi sing 等支持 MRS 的规则系统。

本项目的目标是：  
- 避免传统 GeoIP 国家数据库不准确的问题  
- 提供可直接用于规则匹配的 IP CIDR 集  
- 适合对跨洲路由、分流、低延迟路径选择有要求的使用场景  

---

## 特性

- 📦 **MRS 格式**（体积小、加载快）
- 🌍 **按洲 / 地区拆分**
- 🔁 **每日更新（interval: 86400）**
- 🎯 行为类型：`ipcidr`
- 🧩 可直接作为规则集使用

---

## GeoIP 数据集下载

### 北美 & 欧洲

| 地区 | 说明 | 下载链接 |
|----|----|----|
| 北美洲（NA） | 美国、加拿大等北美地区 IP 段 | https://github.com/agczsz/MRS-IP-EU-NA/raw/refs/heads/main/Continents/NA.mrs |
| 欧洲（EU） | 欧盟及欧洲地区 IP 段 | https://github.com/agczsz/MRS-IP-EU-NA/raw/refs/heads/main/Continents/EU.mrs |

---

### 亚太地区（APAC / Other）

| 地区 | 说明 | 下载链接 |
|----|----|----|
| 香港（HK） | 香港地区 IP 段 | https://github.com/agczsz/MRS-IP-EU-NA/raw/refs/heads/main/Continents/Other/HK.mrs |
| 新加坡（SG） | 新加坡地区 IP 段 | https://github.com/agczsz/MRS-IP-EU-NA/raw/refs/heads/main/Continents/Other/SG.mrs |
| 日本（JP） | 日本地区 IP 段 | https://github.com/agczsz/MRS-IP-EU-NA/raw/refs/heads/main/Continents/Other/JP.mrs |

---

## 适用场景

- 跨洲 / 跨区域流量分流  
- 低延迟路径优选  
- 多出口、多节点路由策略  
- 替代不准确的 GeoIP 国家判断  
- 与 RTT / BGP / 探测策略结合使用  

---

## 说明

- 本项目不依赖传统 GeoIP 国家数据库  
- Anycast 及云厂商 IP 段可能随时间变化  
- 数据仅用于网络分流、研究与学习用途  
