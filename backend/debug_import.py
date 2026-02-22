
try:
    import characters.config
    print("SUCCESS: characters.config imported")
except Exception as e:
    print(f"FAILURE: {e}")
    import characters
    print(f"DEBUG: characters is {characters}")
