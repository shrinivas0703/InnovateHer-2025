from bs4 import BeautifulSoup
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import re
import pandas as pd

def remove_special_characters(input_string: str) -> str:
    # Use regex to keep only letters (a-z, A-Z)
    return re.sub(r'[^a-zA-Z\s]', '', input_string)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for CORS
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/medicaid_info")
async def medicaid_parser():
    url = "https://www.guttmacher.org/state-policy/explore/state-funding-abortion-under-medicaid"

    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"Error fetching URL. Status code: {response.status_code}")
        exit()

    soup = BeautifulSoup(html_content, "html.parser")

    state_info = soup.find("tbody")

    rows = state_info.find_all("tr")
    i = 0
    state_info_map = {}
    for row in rows:
        cells = row.find_all("td")
        if i > 2 and i < 54:
            if cells[2].get_text() != "\xa0":
                state_info_map[remove_special_characters(cells[0].get_text())] = "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and " + cells[2].get_text()
            elif "X" in cells[1].get_text():
                state_info_map[remove_special_characters(cells[0].get_text())] = "Medicaid Funds Provided only for Life Endangerment, Rape and Incest"
            else:
                state_info_map[remove_special_characters(cells[0].get_text())] = "Medicaid Funds for All or Most Medically Necessary Abortions"
        i+=1
    
    for key, val in state_info_map.items():
        if val == "Medicaid Funds Provided only for Life Endangerment, Rape and Incest":
            state_info_map[key] = 0
        if val == "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Fetal impairment":
            state_info_map[key] = 1
        if val == "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Physical health":
            state_info_map[key] = 2
        if "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Physical health, fetal impairment" in val:
            state_info_map[key] = 3
        if val == "Medicaid Funds for All or Most Medically Necessary Abortions":
            state_info_map[key] = 4
    
    num_feature_map = {0: "Medicaid Funds Provided only for Life Endangerment, Rape and Incest",
                       1: "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Fetal impairment",
                       2: "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Physical health",
                       3: "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, Physical health, and Fetal impairment",
                       4: "Medicaid Funds for All or Most Medically Necessary Abortions"}
    
    return JSONResponse(content={"state_info": state_info_map, "num_feature_map": num_feature_map})


@app.get("/abortion_info")
async def medicaid_parser():
    df = pd.read_csv("abortion_data.csv")
    
    status_mapping = {
    "Abortion banned": 0,
    "Gestational limit between 6 and 12 weeks LMP": 1,
    "Gestational limit between 18 and 22 weeks LMP": 2,
    "Gestational limit at or near viability": 3,
    "No gestational limits": 4
    }

    state_abortion_status = dict(zip(df['State'], df['Status of Abortion'].map(status_mapping)))

    status_mapping_swap = {v: k for k, v in status_mapping.items()}
    
    return JSONResponse(content={"state_info": state_abortion_status, "num_feature_map": status_mapping_swap})