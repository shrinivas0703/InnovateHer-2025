from bs4 import BeautifulSoup
import requests
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/medicaid_info', methods=['GET'])
def medicaid_parser():
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
                state_info_map[cells[0].get_text()] = "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and " + cells[2].get_text()
            elif "X" in cells[1].get_text():
                state_info_map[cells[0].get_text()] = "Medicaid Funds Provided only for Life Endangerment, Rape and Incest"
            else:
                state_info_map[cells[0].get_text()] = "Medicaid Funds for All or Most Medically Necessary Abortions"
        i+=1
    
    for key, val in state_info_map.items():
        if val == "Medicaid Funds Provided only for Life Endangerment, Rape and Incest":
            state_info_map[key] = 0
        if val == "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Fetal impairment":
            state_info_map[key] = 1
        if val == "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Physical health":
            state_info_map[key] = 2
        if val == "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, Physical health, and fetal impairment\xa0":
            state_info_map[key] = 3
        if val == "Medicaid Funds for All or Most Medically Necessary Abortions":
            state_info_map[key] = 4
    
    num_feature_map = {0: "Medicaid Funds Provided only for Life Endangerment, Rape and Incest",
                       1: "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Fetal impairment",
                       2: "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, and Physical health",
                       3: "Medicaid Funds Provided only for Life Endangerment, Rape, Incest, Physical health, and Fetal impairment",
                       4: "Medicaid Funds for All or Most Medically Necessary Abortions"}
    
    return jsonify({"state_info": state_info_map, "num_feature_map": num_feature_map})


medicaid_parser()