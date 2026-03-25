# ⚡ PortPulseAfrica — Africa Maritime Intelligence Dashboard

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75?style=flat-square&logo=plotly)
![Countries](https://img.shields.io/badge/Africa-54%20Countries-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Real-time heartbeat of African maritime trade**  
Port calls · Imports & Exports · Cargo flows · 54 African countries · 195+ ports

[🚀 Live Demo](#) · [📓 Data Pipeline](#data-pipeline) · [⚙️ Installation](#installation) · [☁️ Deploy](#deploy)

</div>

---

## 🌍 Overview

**PortPulseAfrica** is an open-source maritime intelligence dashboard built with **Streamlit** and **Plotly**.

It ships with a **pre-filtered African dataset** (`africa_ports_data.csv`) committed in the repo — the dashboard opens instantly with no upload required. You can always upload a fresh file to update the data.

### Data Pipeline

```
Daily_Ports_Data.csv  (full global dataset, on your PC)
         │
         ▼  Run extract_africa_data.ipynb
         │
africa_ports_data.csv  ←── committed in this repo
         │
         ▼  streamlit run app.py  (or Streamlit Cloud)
         │
⚡ PortPulseAfrica Dashboard  — opens instantly, no upload needed
```

---

## ✨ Features

| Tab | Content |
|---|---|
| 🗺️ **Map View** | Choropleth & bubble map + regional pie chart |
| 📈 **Trends** | Monthly flows, YoY growth, trade balance per country |
| 🏆 **Rankings** | Top ports bar chart, country treemap, sortable table |
| 🚢 **Cargo Analysis** | Radar chart, heatmap, stacked cargo breakdown |
| 📊 **Deep Dive** | Scatter, seasonality, raw data + Excel/CSV export |

**Sidebar filters:** Year · Region · Country · Port · Cargo type  
**Downloads:** Formatted Excel (dark theme + Summary sheet) + CSV

---

## ⚙️ Installation

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/portpulseafrica.git
cd portpulseafrica

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
streamlit run app.py
# → Opens http://localhost:8501 with data already loaded ✅
```

---

## ☁️ Deploy on Streamlit Cloud (Free) <a id="deploy"></a>

1. Push this repo to GitHub (including `africa_ports_data.csv`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. **New app** → select `portpulseafrica` → branch `main` → file `app.py`
4. **Deploy** → your URL: `portpulseafrica.streamlit.app` ✅

No server, no configuration, no upload needed — the data is in the repo.

### Update the data

When you have a new `africa_ports_data.csv`:
```bash
# Re-run the notebook to regenerate africa_ports_data.csv, then:
cp F:\AfDB\Momar\Data Port\africa_ports_data.csv .
git add africa_ports_data.csv
git commit -m "📊 Update African ports data — $(date +%Y-%m-%d)"
git push
# Streamlit Cloud redeploys automatically ✅
```

---

## 📁 Project Structure

```
portpulseafrica/
├── app.py                      ← Dashboard (auto-loads africa_ports_data.csv)
├── africa_ports_data.csv       ← Pre-filtered African data (committed)
├── extract_africa_data.ipynb   ← Notebook to regenerate africa_ports_data.csv
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── config.toml             ← Dark theme
```

---

## 🌍 Covered Countries

**54 African Union member states** across 5 regions + 2 French maritime territories.

| Region | Countries |
|---|---|
| North Africa | Algeria, Egypt, Libya, Morocco, Tunisia, Sudan, Mauritania |
| West Africa | Benin, Burkina Faso, Cabo Verde, Côte d'Ivoire, The Gambia, Ghana, Guinea, Guinea-Bissau, Liberia, Mali, Niger, Nigeria, Senegal, Sierra Leone, Togo |
| East Africa | Burundi, Comoros, Djibouti, Eritrea, Ethiopia, Kenya, Madagascar, Mauritius, Mozambique, Rwanda, Seychelles, Somalia, South Sudan, Tanzania, Uganda |
| Central Africa | Cameroon, CAR, Chad, DR Congo, Equatorial Guinea, Gabon, Republic of Congo, São Tomé & Príncipe |
| Southern Africa | Angola, Botswana, Eswatini, Lesotho, Malawi, Namibia, South Africa, Zambia, Zimbabwe |
| + Maritime extras | Mayotte, Réunion |

---

## 📄 License

MIT License © 2026 — PortPulseAfrica

---

<div align="center">
⚡ Built with ❤️ for African maritime decision-makers · <strong>PortPulseAfrica</strong>
</div>
