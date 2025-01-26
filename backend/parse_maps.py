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
async def abortion_parser():
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

@app.get("/gender_affirming_care_info")
async def gender_affirming_care_parser():
    url = "https://www.medpagetoday.com/special-reports/exclusives/104425"

    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.content
    else:
        print(f"Error fetching URL. Status code: {response.status_code}")
        exit()

    soup = BeautifulSoup(html_content, "html.parser")

    state_info = soup.find_all("strong")

    states_and_dc = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
    ]

    # Create a dictionary with the state names as keys and 0 as the value
    overall_count = {state: 4 for state in states_and_dc}
    for state in state_info:
        if "Editor" not in state.get_text():
            overall_count[remove_special_characters(state.get_text())] = 0
    
    num_feature_map = {0: "Banned", 4: "Not Banned"}
    return JSONResponse(content={"state_info": overall_count, "num_feature_map":num_feature_map})
