from osrparse import parse_replay_file
from config import api_key
from circleguard.investigator import Investigator
from circleguard import ReplayPath
from circleguard import Circleguard
from slider import Library
from tkinter import filedialog as fd
import requests
import pyttanko as osu
import tkinter as tk
import pyperclip
import sys
import os

# Hide Tkinter window
tk.Tk().withdraw()

mods = {
    "Mod.NoMod": "NM",
    "Mod.NoFail": "NF",
    "Mod.Easy": "EZ",
    "Mod.TouchDevice": "TD",
    "Mod.Hidden": "HD",
    "Mod.HardRock": "HR",
    "Mod.SuddenDeath": "SD",
    "Mod.DoubleTime": "DT",
    "Mod.Relax": "RX",
    "Mod.HalfTime": "HT",
    "Mod.Nightcore": "NC",
    "Mod.Flashlight": "FL",
    "Mod.AutoPlay": "AT",
    "Mod.SpunOut": "SO",
    "Mod.Relax2": "AP",
    "Mod.Perfect": "PF"
}
modsOrder = ["EZ", "NF", "HT", "HD", "DT", "NC", "HR", "FL", "SD", "PF", "SO", "TD", "RX", "AP", "AT"]
shortMods = ""
shortModsDiff = ""
mapRank = ""
ifRanked = ""
isFC = ""
scorepost = ""
urString = ""
modsString = ""

# Tell user to run setup first and exit the program
if not api_key or not os.path.exists("beatmaps"):
    input("Please run setup before running this!")
    sys.exit()

# Select a replay file and parse it
print("Select a replay file")
try:
    replayPath = fd.askopenfilename(filetypes=[("Replay files", "*.osr")])
    replay = parse_replay_file(replayPath)
except IOError:
    input("Something went wrong opening the file...")
    sys.exit()

# Check if replay contains difficulty increasing or decreasing mods and add to list
for mod in set(replay.mod_combination):
    if mods[str(mod)] == "EZ" or mods[str(mod)] == "HR" or mods[str(mod)] == "DT" or mods[str(mod)] == "NC":
        shortModsDiff += mods[str(mod)]

# Create mod order in a readable way
for mod in modsOrder:
    for x in set(replay.mod_combination):
        if mods[str(x)] == mod:
            shortMods += mods[str(x)]

# Add + in front if the replay has at least 1 mod
if shortMods:
    modsString = " +"

# Get beatmap info
response = requests.get(
    "https://osu.ppy.sh/api/get_beatmaps?k=" + api_key + "&h=" + replay.beatmap_hash + "&mods=" + str(
        osu.mods_from_str(shortModsDiff)))
beatmapInfo = response.json()

# Get leaderboards of beatmap info
response = requests.get(
    "https://osu.ppy.sh/api/get_scores?k=" + api_key + "&b=" + beatmapInfo[0]["beatmap_id"])
leaderboardsInfo = response.json()

# Calculate UR
lb = Library(".\\beatmaps")
bm = lb.lookup_by_id(beatmapInfo[0]["beatmap_id"], download=True, save=True)
cg = Circleguard("8e2c2ed60709996a628da1c66ace5e23c5651d43")
rp = ReplayPath(replayPath)
cg.load(rp)
ur = Investigator.ur(rp.as_list_with_timestamps(), bm)

# Convert UR if DT/NC or HT is used
for x in set(replay.mod_combination):
    if mods[str(x)] == "DT" or mods[str(x)] == "NC":
        ur = ur / 1.5
        urString = " cv."
    elif mods[str(x)] == "HT":
        ur = ur / 0.75
        urString = " cv."

# Get rank of replay on map's leaderboard
for idx, score in enumerate(leaderboardsInfo):
    if replay.player_name == score["username"]:
        mapRank = " #" + str(idx + 1)

# Calculate pp
pp, _, _, _, _ = osu.ppv2(aim_stars=float(beatmapInfo[0]["diff_aim"]), speed_stars=float(beatmapInfo[0]["diff_speed"]),
                          max_combo=int(beatmapInfo[0]["max_combo"]), nsliders=int(beatmapInfo[0]["count_slider"]),
                          ncircles=int(beatmapInfo[0]["count_normal"]), nobjects=int(beatmapInfo[0]["count_slider"]) +
                                                                                 int(beatmapInfo[0][
                                                                                         "count_normal"]) + int(
        beatmapInfo[0]["count_spinner"]),
                          base_ar=float(beatmapInfo[0]["diff_approach"]), base_od=float(beatmapInfo[0]["diff_overall"]),
                          mode=int(beatmapInfo[0]["mode"]), mods=osu.mods_from_str(shortMods), combo=replay.max_combo,
                          n300=replay.number_300s, n100=replay.number_100s, n50=replay.number_50s, nmiss=replay.misses,
                          score_version=1)
pp = round(float("%g" % pp))

# Calculate accuracy
accuracy = (50 * replay.number_50s + 100 * replay.number_100s + 300 * replay.number_300s) / (
        300 * (replay.misses + replay.number_50s + replay.number_100s + replay.number_300s))

# Add 'if ranked' if the map is not ranked or approved
if not (beatmapInfo[0]["approved"] == "1" or beatmapInfo[0]["approved"] == "2"):
    ifRanked = " if ranked"

# Check if it's an FC otherwise get combo of replay/max combo
if replay.is_perfect_combo:
    isFC = " FC"
else:
    if replay.misses > 0:
        isFC = " " + str(replay.misses) + "m " + str(replay.max_combo) + "/" + beatmapInfo[0]["max_combo"] + "x"
    else:
        isFC = " " + str(replay.max_combo) + "/" + beatmapInfo[0]["max_combo"] + "x"

# Scorepost text
scorepost = (replay.player_name + " | " + beatmapInfo[0]["artist"] + " - " + beatmapInfo[0]["title"] + " [" +
             beatmapInfo[0]["version"] + "]" + modsString + shortMods + " (" + str(
            round(float(beatmapInfo[0]["difficultyrating"]), 2)) + "*) " + str(
            round(accuracy * 100, 2)) + "%" + isFC + mapRank + " | " + str(pp) + "pp" + ifRanked + " | " +
             str(round(ur, 2)) + urString + " UR")

# Copy scorepost to clipboard
pyperclip.copy(scorepost)

# Add some extra text and wait for user input to close
input("\n╔" + "═" * len(scorepost) + "╗\n║" + scorepost + "║\n╚" + "═" * len(scorepost) + "╝" +
      "\n\nScorepost has been copied to your clipboard!")
