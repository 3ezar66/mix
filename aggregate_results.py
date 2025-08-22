import json
import miner_discovery
import read_ds18b20
import wifi_scanner

def main():
    suspects = miner_discovery.main_return()
    with open('suspects.json', 'w') as f:
        json.dump(suspects, f)

    temp = read_ds18b20.read_temp()
    with open('temps.json', 'w') as f:
        json.dump([temp], f)

    wifi = wifi_scanner.scan_wifi()
    with open('wifi.json', 'w') as f:
        json.dump(wifi, f)

if __name__ == "__main__":
    main()