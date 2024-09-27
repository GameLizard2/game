import random

# Функция для печати текста с отступом
def print_tab(spaces, text):
    print(" " * spaces + text)

# Функция для вывода вступительной информации
def intro():
    print_tab(24, "DEEPSPACE")
    print_tab(20, "CREATIVE COMPUTING")
    print_tab(18, "MORRISTOWN, NEW JERSEY")
    print("\n" * 3)
    print("THIS IS DEEPSPACE, A TACTICAL SIMULATION OF SHIP TO SHIP")
    print("COMBAT IN DEEP SPACE.")

# Функция для запроса инструкций у пользователя
def ask_instructions():
    return input("DO YOU WISH INSTRUCTIONS (YES/NO): ").strip().upper()

# Функция для вывода инструкций
def show_instructions():
    print("\nYou are a captain assigned to patrol your empire's borders against hostile aliens.")
    print("You will select a ship and equip it with weapons, then engage in combat.")
    print("\nShips have the following characteristics:")
    print("TYPE        SPEED   CARGO SPACE   PROTECTION")
    print("1. SCOUT     10X        16            1")
    print("2. CRUISER    4X        24            2")
    print("3. BATTLESHIP 2X        30            5")
    print("\nSPEED is relative, CARGO SPACE determines how much weaponry you can carry,")
    print("and PROTECTION refers to the strength of your armor and shields.\n")

# Функция для выбора корабля
def choose_ship():
    print("\nChoose a ship:")
    print("1. SCOUT")
    print("2. CRUISER")
    print("3. BATTLESHIP")
    while True:
        try:
            choice = int(input("Select a ship (1-3): "))
            if choice in [1, 2, 3]:
                return choice
        except ValueError:
            pass
        print("Invalid choice, please select 1, 2, or 3.")

# Функция для получения характеристик выбранного корабля
def ship_stats(choice):
    if choice == 1:
        return {'speed': 10, 'cargo_space': 16, 'protection': 1}
    elif choice == 2:
        return {'speed': 4, 'cargo_space': 24, 'protection': 2}
    elif choice == 3:
        return {'speed': 2, 'cargo_space': 30, 'protection': 5}

# Функция для показа списка доступного оружия
def show_weapons():
    print("\nChoose your weaponry:")
    print("TYPE                         CARGO SPACE    REL. STRENGTH")
    print("1. PHASER BANKS                   12                4")
    print("2. ANTI-MATTER MISSILE             4               20")
    print("3. HYPERSPACE LANCE                4               16")
    print("4. PHOTON TORPEDO                  2               10")
    print("5. HYPERON NEUTRALIZATION FIELD   20                6")

# Функция для загрузки оружия на корабль
def load_weapons(cargo_space):
    weapons = {
        1: {'name': 'Phaser Banks', 'cargo': 12, 'strength': 4},
        2: {'name': 'Anti-Matter Missile', 'cargo': 4, 'strength': 20},
        3: {'name': 'Hyperspace Lance', 'cargo': 4, 'strength': 16},
        4: {'name': 'Photon Torpedo', 'cargo': 2, 'strength': 10},
        5: {'name': 'Hyperon Neutralization Field', 'cargo': 20, 'strength': 6},
    }
    loadout = []
    while cargo_space > 0:
        show_weapons()
        weapon_choice = int(input(f"Choose a weapon (1-5), remaining cargo space: {cargo_space}: "))
        if weapon_choice in weapons:
            weapon_qty = int(input(f"How many {weapons[weapon_choice]['name']}? "))
            total_cargo = weapon_qty * weapons[weapon_choice]['cargo']
            if total_cargo <= cargo_space:
                loadout.append((weapon_choice, weapon_qty))
                cargo_space -= total_cargo
            else:
                print("Not enough cargo space.")
        else:
            print("Invalid weapon choice.")
    return loadout

# Основная функция игры
def main():
    intro()
    if ask_instructions() == "YES":
        show_instructions()

    ship_choice = choose_ship()
    stats = ship_stats(ship_choice)
    print(f"\nYou selected a ship with {stats['cargo_space']} units of cargo space.")

    loadout = load_weapons(stats['cargo_space'])
    print("\nYour ship is ready for battle with the following loadout:")
    for weapon, qty in loadout:
        print(f"{qty} units of Weapon {weapon}")

    # Логика игры продолжается здесь...

if __name__ == "__main__":
    main()
