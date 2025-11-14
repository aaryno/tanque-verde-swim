#!/usr/bin/env python3
"""
Add 2025 State Championship relay results to relay records
"""

# Results from 2025 AIA D3 State Championship (Nov 8, 2025)
STATE_RELAYS_2025 = [
    {
        "gender": "girls",
        "event": "200 MEDLEY RELAY",
        "time": "2:00.57",
        "place": 6,
        "date": "Nov 08, 2025",
        "meet": "2025 D-3 AIA State Championships (AZ)",
        "participants": "Logan Sulger (SR), Adrianna Witte (SR), Hadley Cusson (JR), Isla Cerepak (FR)"
    },
    {
        "gender": "boys",
        "event": "200 MEDLEY RELAY",
        "time": "1:42.70",
        "place": 4,
        "date": "Nov 08, 2025",
        "meet": "2025 D-3 AIA State Championships (AZ)",
        "participants": "Kent Olsson (FR), Wade Olsson (JR), Zachary Duerkop (SR), Grayson The (SR)"
    },
    {
        "gender": "girls",
        "event": "200 FREE RELAY",
        "time": "1:48.54",
        "place": 7,
        "date": "Nov 08, 2025",
        "meet": "2025 D-3 AIA State Championships (AZ)",
        "participants": "Hadley Cusson (JR), Isla Cerepak (FR), Stella Eftekhar (FR), Logan Sulger (SR)"
    },
    {
        "gender": "boys",
        "event": "200 FREE RELAY",
        "time": "1:30.45",
        "place": 1,
        "date": "Nov 08, 2025",
        "meet": "2025 D-3 AIA State Championships (AZ)",
        "participants": "Wade Olsson (JR), Jackson Eftekhar (JR), Grayson The (SR), Zachary Duerkop (SR)"
    },
    {
        "gender": "girls",
        "event": "400 FREE RELAY",
        "time": "4:00.33",
        "place": 11,
        "date": "Nov 08, 2025",
        "meet": "2025 D-3 AIA State Championships (AZ)",
        "participants": "Hadley Cusson (JR), Isla Cerepak (FR), Ella Bissmeyer (SO), Talia Schwab (FR)"
    },
    {
        "gender": "boys",
        "event": "400 FREE RELAY",
        "time": "3:25.97",
        "place": 5,
        "date": "Nov 08, 2025",
        "meet": "2025 D-3 AIA State Championships (AZ)",
        "participants": "Wade Olsson (JR), Jackson Machamer (JR), Kent Olsson (FR), Jackson Eftekhar (JR)"
    },
]

if __name__ == "__main__":
    print("2025 AIA D3 State Championship Relay Results")
    print("=" * 70)
    for relay in STATE_RELAYS_2025:
        print(f"\n{relay['gender'].upper()} {relay['event']}")
        print(f"  Time: {relay['time']} (Place: {relay['place']})")
        print(f"  Swimmers: {relay['participants']}")
        print(f"  {relay['date']} at {relay['meet']}")

