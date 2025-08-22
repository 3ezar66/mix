import csv
import json

input_file = "ir.csv"
output_file = "iran_isp_ip_ranges.full.json"

ranges = {}
with open(input_file, encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 5:
            continue
        ip_start, ip_end, count, date, isp = [x.strip() for x in row]
        if not isp:
            isp = "Unknown"
        # دسته‌بندی بر اساس ISP
        if isp not in ranges:
            ranges[isp] = []
        ranges[isp].append({
            "start_ip": ip_start,
            "end_ip": ip_end,
            "count": int(count),
            "date": date
        })

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(ranges, f, indent=2, ensure_ascii=False)

print(f"Done! Exported {len(ranges)} ISPs and all their ranges to {output_file}")