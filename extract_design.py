import json

with open("/Users/macbookair/.gemini/antigravity-ide/brain/4081975e-b656-4910-a653-d40a6c081c93/.system_generated/steps/268/output.txt", "r") as f:
    project_data = json.load(f)

design_md = project_data.get("designTheme", {}).get("designMd", "")

if design_md:
    output_path = "/Users/macbookair/CODING/VITALS.IO/Vitals_Institutional_Redesign/Design_System_asset-stub-assets_b7f36c89c5e74ac3ae201a0e291109a5.md"
    with open(output_path, "w") as f:
        f.write(design_md)
    print("Saved Design System Markdown.")
else:
    print("Design System Markdown not found.")
