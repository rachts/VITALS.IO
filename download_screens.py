import json
import os
import subprocess

with open("/Users/macbookair/.gemini/antigravity-ide/brain/4081975e-b656-4910-a653-d40a6c081c93/.system_generated/steps/258/output.txt", "r") as f:
    data = json.load(f)

output_dir = "/Users/macbookair/CODING/VITALS.IO/Vitals_Institutional_Redesign"
os.makedirs(output_dir, exist_ok=True)

for screen in data.get("screens", []):
    title = screen.get("title", "Untitled").replace(" | ", "_").replace(" ", "_").replace(".", "_")
    screen_id = screen["name"].split("/")[-1]
    
    # Download HTML
    html_url = screen.get("htmlCode", {}).get("downloadUrl")
    if html_url:
        print(f"Downloading HTML for {title}...")
        subprocess.run(["curl", "-L", "-s", html_url, "-o", f"{output_dir}/{title}_{screen_id}.html"])
        
    # Download Screenshot
    screenshot_url = screen.get("screenshot", {}).get("downloadUrl")
    if screenshot_url:
        print(f"Downloading Screenshot for {title}...")
        subprocess.run(["curl", "-L", "-s", screenshot_url, "-o", f"{output_dir}/{title}_{screen_id}.png"])

print("Download complete for screens in list_screens.")
