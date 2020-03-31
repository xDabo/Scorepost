import os
import sys

# Create beatmaps directory
if not os.path.exists("beatmaps"):
    os.mkdir("beatmaps")

# Write api key to config file
f = open("config.py", "w")
f.write("api_key=\"" + input("Please enter your api key: ") + "\"")
f.close()
input("api key succesfully updated!")
if os.path.exists("setup.py"):
    os.rename("setup.py", "set_api_key.py")
sys.exit()
