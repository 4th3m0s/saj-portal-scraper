# SAJ Portal Scraper Add-on for Home Assistant

> **Disclaimer:** I'm not a developer — this is my first Home Assistant add-on and also my first GitHub repository. I built this project to solve my own problem and decided to share it in case it helps others as well.

This Home Assistant add-on enables automated retrieval of live data from the **SAJ Solar Portal** using **Playwright**, and publishes the filtered values via **MQTT**.

---

## 🚀 Features

**Tested Portal:** This add-on has only been tested with the SAJ portal URL:

```
https://eop.saj-electric.com
```

Other SAJ portal instances or regional servers may behave differently. Compatibility with those servers cannot be guaranteed.

**Note:** SAJ does *not* provide an official API. This add-on exclusively uses publicly visible network requests of the web portal that occur during a normal user login in a browser. No security mechanisms are bypassed, and no private API endpoints are accessed.

* Automatic login to the SAJ web portal via Playwright
* Captures the HTTP response `getDeviceEneryFlowData`
* Filters the returned JSON data based on `filter_fields.json`
* Publishes the filtered data via MQTT
* Error detection with automatic screenshots (keeps only the 5 newest screenshots)
* Configurable scan time, MQTT settings, and SAJ portal URL

---

## 🔧 How It Works & Parameter Explanation

The add-on performs an automated login to the SAJ portal and waits for the network request `getDeviceEneryFlowData`, which contains the current energy and status data of the inverter.

Only when this request occurs inside the portal, the data is collected, filtered, and published via MQTT.

### Configuration Fields Explained

Below is the full list of configuration options supported by the add-on:

| Field              | Description                                                   |
| ------------------ | ------------------------------------------------------------- |
| `saj_username`     | Login name or email for the SAJ portal                        |
| `saj_password`     | Password for the SAJ portal                                   |
| `saj_url`          | SAJ portal URL (default: `https://eop.saj-electric.com`)      |
| `scan_time`        | Time in seconds to wait **after login** before capturing data |
| `scan_interval`    | Interval (seconds) between each full scan run                 |
| `mqtt_broker`      | Hostname/IP of the MQTT broker                                |
| `mqtt_port`        | MQTT port (default: 1883)                                     |
| `mqtt_username`    | Optional MQTT username                                        |
| `mqtt_password`    | Optional MQTT password                                        |
| `mqtt_topic`       | Topic used to publish filtered data                           |
| `mqtt_device_name` | Friendly MQTT device name for Home Assistant                  |


## 📦 Installation

### Adding the Repository

1. Open your Home Assistant UI.
2. Navigate to **Settings → Add-ons → Add-on Store**.
3. In the top-right corner, open the **⋮ menu** and select **Repositories**.
4. Add the GitHub repository URL:

   ```
   https://github.com/4th3m0s/saj_portal_scraper
   ```
5. Confirm and close the dialog.

### Installing the Add-on

1. Refresh the Add-on Store page (a hard refresh like **Ctrl+Shift+R** / **Cmd+Shift+R** may help).
2. You should now see **SAJ Portal Scraper** listed under your added repositories.
3. Open the add-on page and click **Install**.
4. After installation, adjust its configuration as needed and start the add-on.

---

## 🔍 How the Add-on Works Internally

### 1. Login via Playwright

* A headless Chromium browser is launched
* The login form is filled out and submitted automatically

### 2. Capturing the HTTP Request

The add-on listens for responses containing:

```
getDeviceEneryFlowData
```

The captured JSON data is then:

* filtered
* logged
* published via MQTT

### 3. Error Handling

If no login or no data is received:

* A screenshot is saved
* Only the **five most recent** error screenshots are kept

---
