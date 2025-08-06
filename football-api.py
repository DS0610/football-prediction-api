from datetime import datetime, timedelta, timezone
import os
import requests
import pytz


# FOOTBALLPREDICT_API KEY
API_KEY = os.getenv("FOOTBALLPREDICT_API_KEY")
url = "https://football-prediction-api.p.rapidapi.com/api/v2/list-markets"

headers = {
    "X-RapidAPI-Key": API_KEY
}

# README 파일 경로
README_PATH = "README.md"

api_tz = pytz.timezone("Europe/London")
local_tz = pytz.timezone("Asia/Seoul")

def get_current_datetime_on_api_server():
    london_time = datetime.now(tz=timezone.utc).astimezone(api_tz)
    return london_time

def to_local_datetime(start_date):
    dt = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    return api_tz.localize(dt).astimezone(local_tz)

def get_predictions():
    current_server_time = get_current_datetime_on_api_server()
    tomorrow = current_server_time.date() + timedelta(days=1)

    headers = {
        'User-Agent': 'python_requests',
        "X-RapidAPI-Key": os.environ["API_KEY"],
    }
    params = {
        "iso_date": tomorrow.isoformat(),
        "federation": "UEFA",
        "market": "classic"
    }

    prediction_endpoint = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"
    response = requests.get(prediction_endpoint, headers=headers, params=params)

    if response.ok:
        json = response.json()
        json["data"].sort(key=lambda p: p["start_date"])
        return json["data"], tomorrow
    else:
        print("Bad response from server, status-code: {}".format(response.status_code))
        print(response.content)
        return [], tomorrow

def write_readme(matches, date):
    now = datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")
    readme_content = f"# ⚽️ UEFA 축구 경기 예측 결과\n\n"
    readme_content += f"**예측 날짜:** {date} (Europe/London)\n\n"
    readme_content += f"⏳ 업데이트 시간: {now} (Asia/Seoul)\n\n"
    readme_content += "| 경기 시간(한국) | 홈팀 | 어웨이팀 | 예측 | 배당률(odds) |\n"
    readme_content += "|:-------------:|:-----:|:-------:|:-----:|:------------:|\n"

    if not matches:
        readme_content += "| 데이터 없음 |  |  |  |  |\n"
    else:
        for match in matches:
            local_start_time = to_local_datetime(match["start_date"]).strftime("%Y-%m-%d %H:%M")
            home_team = match["home_team"]
            away_team = match["away_team"]
            prediction = match["prediction"]
            odds = match.get("odds", {}).get(prediction, "-")
            readme_content += f"| {local_start_time} | {home_team} | {away_team} | {prediction} | {odds} |\n"

    readme_content += "\n---\n자동 업데이트 봇에 의해 관리됩니다.\n"
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

if __name__ == "__main__":
    matches, date = get_predictions()
    write_readme(matches, date)
