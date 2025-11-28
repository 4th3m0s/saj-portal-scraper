from playwright.sync_api import sync_playwright, Playwright
import time
import json
from datetime import datetime
import paho.mqtt.client as mqtt
from importlib.metadata import version
import sys

#print("-----------------------------------------------------------------------------------")
#print("playwright version:", version("playwright"))
#print("paho-mqtt version:", version("paho-mqtt"))


if "-v" in sys.argv:
        print("-----------------------------------------------------------------------------------")
        print("playwright version:", version("playwright"))
        print("paho-mqtt version:", version("paho-mqtt"))
        sys.exit(0)


def load_config(config_file="/data/options.json"):
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Config Error: {e}")
        return None


def load_filter_fields(filter_file="filter_fields.json"):
    try:
        with open(filter_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Filter Error: {e}")
        return None


def load_sensor_definitions(sensor_file="sensor_definitions.json"):
    try:
        with open(sensor_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Sensor Definitions Error: {e}")
        return None


def filter_json_data(json_data, filter_fields):
    if not json_data or not filter_fields:
        return {}

    filtered_data = {}
    if 'data' in json_data and isinstance(json_data['data'], dict):
        for field in filter_fields:
            if field in json_data['data']:
                filtered_data[field] = json_data['data'][field]

    # errCode + errMsg prüfen
    for field in ['errCode', 'errMsg']:
        if field in json_data and field in filter_fields:
            filtered_data[field] = json_data[field]

    return filtered_data


def setup_mqtt_client(config):
    try:
        client = mqtt.Client()
        if config.get('mqtt_username'):
            client.username_pw_set(config.get('mqtt_username'), config.get('mqtt_password', ''))

        client.connect(config.get('mqtt_broker'), config.get('mqtt_port', 1883), 60)
        print("✅ MQTT connected")
        return client
    except Exception as e:
        print(f"❌ MQTT Error: {e}")
        return None


def publish_mqtt_data(client, config, filtered_data):
    if not client:
        return False

    try:
        payload = json.dumps(filtered_data, ensure_ascii=False)
        result = client.publish(config.get('mqtt_topic', 'saj/solar/data'), payload)
        if result.rc == 0:
            print("📡 Data published")
            return True
        return False
    except Exception as e:
        print(f"❌ MQTT Send Error: {e}")
        return False


def run(playwright: Playwright):
    config = load_config()
    if not config:
        return

    filter_fields = load_filter_fields()
    sensor_definitions = load_sensor_definitions()
    if not filter_fields or not sensor_definitions:
        return

    username = config.get("saj_username")
    password = config.get("saj_password")
    saj_url = config.get("saj_url", "https://eop.saj-electric.com")

    if not username or not password:
        print("❌ No user/password found!")
        return

    mqtt_client = setup_mqtt_client(config)

    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    all_responses = []
    login_successful = False

    def handle_response(response):
        if "getDeviceEneryFlowData" in response.url:
            try:
                json_data = response.json()
                filtered_data = filter_json_data(json_data, filter_fields)

                nonlocal login_successful
                login_successful = True

                print(f"📊 Values received: {len(filtered_data)}")

                if mqtt_client and filtered_data:
                    publish_mqtt_data(mqtt_client, config, filtered_data)

                all_responses.append(filtered_data)
            except Exception as e:
                print(f"❌ Response Error: {e}")

    page.on("response", handle_response)

    # Login
    page.goto(f"{saj_url}/login")
    page.wait_for_timeout(1000)
    page.get_by_role("textbox", name="Username/Email").fill(username)
    page.get_by_role("textbox", name="Please enter your password").fill(password)
    page.get_by_role("button", name="Login").click()

    # Waitn
    wait_time = config.get("scan_time", 30)
    print(f"⏳ Wait {wait_time}s for data…")
    page.wait_for_timeout(wait_time * 1000)
    page.remove_listener("response", handle_response)

    print(f"\n✅ {len(all_responses)} Responses received")

    if not login_successful:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_file = f"{config.get('screenshot_path', '/addon_configs/local_saj-scraper/screenshot')}_failed_{timestamp}.png"
        page.screenshot(path=screenshot_file)
        print(f"📸 Screenshot saved: {screenshot_file}")
        # === Nur die 5 neuesten Screenshots behalten ===
        directory = os.path.dirname(base_path)  # Ordner extrahieren
        files = sorted(
            glob(os.path.join(directory, "*_failed_*.png")),
            key=os.path.getmtime,
            reverse=True
        )
    
        # Alle außer den ersten 5 löschen
        for old_file in files[5:]:
            try:
                os.remove(old_file)
                print(f"🗑️ Deleted old screenshot: {old_file}")
            except Exception as e:
                print(f"⚠️ Error deleting file {old_file}: {e}")    
        
        
        

    if mqtt_client:
        mqtt_client.disconnect()

    browser.close()


with sync_playwright() as playwright:
    run(playwright)
