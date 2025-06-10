import pickle

colors = {}

colors["yellow"] = 17
colors["green"] = 17
colors["purple"] = 17
colors["orange"] = 17
colors["red"] = 17
colors["blue"] = 17

colors_rgb = {}

for key in list(colors.keys()):
    colors_rgb[key]=0
    


colors_rgb["yellow"] = "#daca50"
colors_rgb["green"] = "#368955"
colors_rgb["purple"] = "#3c2e6c"
colors_rgb["orange"] = "#d4782f"
colors_rgb["red"] = "#9b3241"
colors_rgb["blue"] = "#2f91b6"


with open("colors2eq.pickle", "wb") as f:
    pickle.dump(colors, f)
with open("colors_rgb2eq.pickle", "wb") as f:
    pickle.dump(colors_rgb, f)
    
with open('colors2eq.pickle', 'rb') as f:
    b = pickle.load(f)

print(b==colors)

with open('colors_rgb2eq.pickle', 'rb') as f:
    b = pickle.load(f)
    
print(b==colors_rgb)