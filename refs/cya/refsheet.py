cya_path = "refs/cya/"
max_hp = 25
mob_kill_restore = 3
destination_restore = 7
potion = 7
potion_greater = 11
upgrade_att = 1
upgrade_def = 2

bandit = {
    "Bandit",
    1,
    9,
    9
}

mimic = {
    "Mimic",
    1,
    10,
    8
}

orc = {
    "Orc",
    1,
    10,
    9
}

skeleton = {
    "Skeleton",
    1,
    4,
    5
}

trader_joe = {
    "Trader Joe",
    1,
    10,
    4
}

final_boss = {
    "Nothic",
    2,
    15,
    12
}

with open(f"{cya_path}Char_Sheet.txt") as file:
    script_char_sheet = file.readlines()

with open(f"{cya_path}Cabb_Scene.txt") as file:
    script_cabb_scene = file.readlines()

with open(f"{cya_path}Lab_Maze.txt") as file:
    script_lab_maze = file.readlines()

with open(f"{cya_path}Fights_Etc.txt") as file:
    script_fights_etc = file.readlines()

with open(f"{cya_path}End_Scene.txt") as file:
    script_end_scene = file.readlines()

with open(f"{cya_path}Credits.txt"):
    script_credits = file.readlines()
