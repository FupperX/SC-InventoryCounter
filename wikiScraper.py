import requests
import json

def getAllInCategory(category):
    membersReq = requests.get("https://starcitizen.tools/api.php?action=query&format=json&list=categorymembers&cmlimit=500&cmtitle=Category:" + category)
    membersJson = json.loads(membersReq.content)

    members = [obj["title"] for obj in membersJson["query"]["categorymembers"] if obj["ns"] == 0]
    return members

categories = [
    "Personal_weapons", 
    "Helmets", "Torso_armor", "Arms_armor", "Legs_armor", "Backpacks", "Undersuits", 
    "Optics_attachments",
    "Personal_utility_items"]

f = open("truth.txt", "w")

for cat in categories:
    results = getAllInCategory(cat)
    print(cat + ": ", results)

    for r in results:
        f.write(r + "\n")

f.close()
