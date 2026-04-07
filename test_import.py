try:
    from wtpsplit import SaT
    with open("d:/vsplayG/nlpapp/test_result.txt", "w") as f:
        f.write("SUCCESS: SaT imported\n")
except ImportError as e:
    with open("d:/vsplayG/nlpapp/test_result.txt", "w") as f:
        f.write(f"FULL_ERROR: {str(e)}\n")
        f.write(f"REPR: {repr(e)}\n")
        import traceback
        f.write(traceback.format_exc())
