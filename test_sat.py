import sys
import traceback

try:
    from wtpsplit import SaT
    print("SUCCESS: SaT imported")
except ImportError as e:
    with open("test_sat_trace.txt", "w", encoding="utf-8") as f:
        f.write(f"IMPORT ERROR: {e}\n")
        traceback.print_exc(file=f)

