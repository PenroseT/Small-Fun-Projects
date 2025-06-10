import pickle

colors = {}

colors["yellow"] = 10
colors["green"] = 20
colors["purple"] = 19
colors["orange"] = 18
colors["red"] = 18
colors["blue"] = 21

colors_rgb = {}

for key in list(colors.keys()):
    colors_rgb[key]=0
    


colors_rgb["yellow"] = "#daca50"
colors_rgb["green"] = "#368955"
colors_rgb["purple"] = "#3c2e6c"
colors_rgb["orange"] = "#d4782f"
colors_rgb["red"] = "#9b3241"
colors_rgb["blue"] = "#2f91b6"


with open("colors2.pickle", "wb") as f:
    pickle.dump(colors, f)
with open("colors_rgb2.pickle", "wb") as f:
    pickle.dump(colors_rgb, f)
    
with open('colors2.pickle', 'rb') as f:
    b = pickle.load(f)

print(b==colors)

with open('colors_rgb2.pickle', 'rb') as f:
    b = pickle.load(f)
    
print(b==colors_rgb)