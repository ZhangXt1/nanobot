---
name: weather
description: Get current weather and forecasts from Moji Weather (no API key required).
homepage: http://tianqi.moji.com/
metadata: {"nanobot":{"emoji":"🌤️","requires":{"bins":["curl","grep","sed"]}}}
---

# Weather

Get weather information from Moji Weather (墨迹天气), no API keys needed.

## Moji Weather (primary)

### Get weather for a city

Format: `http://tianqi.moji.com/weather/china/<province>/<city>`

### Bash Commands
Example for Shanghai:
```bash
# Get current weather
curl -s "http://tianqi.moji.com/weather/china/shanghai" | grep -oP '(?<=class="wea_weather">).*?(?=</div>)' | head -1
# Output: 晴

# Get current temperature
curl -s "http://tianqi.moji.com/weather/china/shanghai" | grep -oP '(?<=class="wea_temperature"><em>).*?(?=</em>)'
# Output: 15

# Get weather description
curl -s "http://tianqi.moji.com/weather/china/shanghai" | grep -oP '(?<=class="wea_about">).*?(?=</div>)' | head -1 | sed 's/\s\+//g'
# Output: 空气优湿度：45%

# Get full forecast
curl -s "http://tianqi.moji.com/weather/china/shanghai" | grep -A 10 -B 2 "class=\"forecast\""
```

### PowerShell Commands
Example for Shanghai:
```powershell
# Get weather page content
$content = Invoke-WebRequest -Uri "http://tianqi.moji.com/weather/china/shanghai" -UseBasicParsing

# Extract weather information using simple string operations
# Note: This method may need adjustment if the page structure changes
$content.Content | Select-String -Pattern "<div class=\"wea_weather\">.*?</div>" -AllMatches | ForEach-Object { $_.Matches.Value -replace '<[^>]+>', '' }

# Extract temperature information
$content.Content | Select-String -Pattern "<div class=\"wea_temperature\"><em>.*?</em>" -AllMatches | ForEach-Object { $_.Matches.Value -replace '<[^>]+>', '' }

# Extract weather description
$content.Content | Select-String -Pattern "<div class=\"wea_about\">.*?</div>" -AllMatches | ForEach-Object { $_.Matches.Value -replace '<[^>]+>', '' }

# Get full page content for detailed analysis
$content.Content
```

### Tips:
- Replace `<province>` and `<city>` with the actual province and city names in Chinese
- Use URL-encoded city names if they contain spaces
- The output may require additional parsing depending on the specific information needed
- For more detailed weather information, you can scrape additional elements from the page
- Use Bash commands on Linux/macOS and PowerShell commands on Windows

## Fallback: wttr.in

If Moji Weather is unavailable, you can use wttr.in as a fallback:

```bash
curl -s "wttr.in/<city>?format=3"
# Output: <city>: ⛅️ +8°C
```
