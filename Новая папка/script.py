from browser import document

# Переменные для отслеживания состояния
ship_stats = {'speed': 0, 'cargo_space': 0, 'protection': 0}
cargo_used = 0
weapons = {
    1: {'name': 'Phaser Banks', 'cargo': 12, 'strength': 4},
    2: {'name': 'Anti-Matter Missile', 'cargo': 4, 'strength': 20},
    3: {'name': 'Hyperspace Lance', 'cargo': 4, 'strength': 16},
    4: {'name': 'Photon Torpedo', 'cargo': 2, 'strength': 10},
}
loadout = []

# Функция для вывода текста в консоль
def print_text(text):
    console = document["console"]
    console.innerHTML += text + "<br>"
    console.scrollTop = console.scrollHeight  # Автопрокрутка вниз

# Функция для получения пользовательского ввода
def get_input(prompt_text, callback):
    print_text(prompt_text)
    input_field = document["user_input"]
    submit_button = document["submit_button"]

    def on_submit(event):
        user_input = input_field.value.strip()
        input_field.value = ""  # Очищаем поле ввода
        submit_button.unbind("click", on_submit)  # Убираем событие для кнопки
        callback(user_input)  # Передача пользовательского ввода в обработчик

    submit_button.bind("click", on_submit)

# Основная логика игры
def game_intro():
    print_text("DEEPSPACE<br>CREATIVE COMPUTING<br>MORRISTOWN, NEW JERSEY<br><br>")
    print_text("THIS IS DEEPSPACE, A TACTICAL SIMULATION OF SHIP TO SHIP COMBAT IN DEEP SPACE.<br>")
    print_text("You are a captain assigned to patrol your empire's borders against hostile aliens.")
    print_text("You will select a ship and equip it with weapons, then engage in combat.<br>")
    print_text("Ships have the following characteristics:")
    print_text("TYPE        SPEED   CARGO SPACE   PROTECTION")
    print_text("1. SCOUT     10X        16            1")
    print_text("2. CRUISER    4X        24            2")
    print_text("3. BATTLESHIP 2X        30            5")
    print_text("<br>Select a ship (1-3):")
    get_input("Choose a ship (1-3):", choose_ship)

# Обработка выбора корабля
def choose_ship(choice):
    global ship_stats
    if choice in ['1', '2', '3']:
        ship_choice = int(choice)
        if ship_choice == 1:
            ship_stats = {'speed': 10, 'cargo_space': 16, 'protection': 1}
            print_text("You selected the SCOUT.")
        elif ship_choice == 2:
            ship_stats = {'speed': 4, 'cargo_space': 24, 'protection': 2}
            print_text("You selected the CRUISER.")
        elif ship_choice == 3:
            ship_stats = {'speed': 2, 'cargo_space': 30, 'protection': 5}
            print_text("You selected the BATTLESHIP.")
        # Переходим к выбору оружия
        choose_weapons()
    else:
        print_text("Invalid choice. Please select 1, 2, or 3.")
        get_input("Choose a ship (1-3):", choose_ship)

# Функция выбора оружия с учётом оставшегося грузового пространства
def choose_weapons():
    global cargo_used
    if cargo_used < ship_stats['cargo_space']:
        print_text("<br>Now, select your weapons (available cargo space: {}):".format(ship_stats['cargo_space'] - cargo_used))
        print_text("1. PHASER BANKS (Cargo: 12, Strength: 4)")
        print_text("2. ANTI-MATTER MISSILE (Cargo: 4, Strength: 20)")
        print_text("3. HYPERSPACE LANCE (Cargo: 4, Strength: 16)")
        print_text("4. PHOTON TORPEDO (Cargo: 2, Strength: 10)")
        get_input("Choose a weapon (1-4):", weapon_choice)
    else:
        print_text("Cargo space is full. Prepare for battle!")
        # Переход к бою
        start_battle()

# Обработка выбора оружия
def weapon_choice(choice):
    global cargo_used, loadout
    if choice in ['1', '2', '3', '4']:
        weapon_choice = int(choice)
        weapon = weapons[weapon_choice]

        # Проверяем, есть ли уже это оружие в списке
        if any(w['name'] == weapon['name'] for w in loadout):
            print_text(f"You already have {weapon['name']} in your loadout. Choose another weapon.")
            choose_weapons()
            return

        # Проверка на доступное место
        if cargo_used + weapon['cargo'] <= ship_stats['cargo_space']:
            loadout.append(weapon)
            cargo_used += weapon['cargo']
            print_text(f"You have chosen {weapon['name']}. Remaining cargo space: {ship_stats['cargo_space'] - cargo_used}")
            choose_weapons()
        else:
            print_text("Not enough cargo space for this weapon.")
            choose_weapons()
    else:
        print_text("Invalid choice. Please select 1-4.")
        get_input("Choose a weapon (1-4):", weapon_choice)

# Переход к бою
def start_battle():
    # Создаём врага
    enemy = {
        'name': 'Alien Destroyer',
        'health': 50,  # Здоровье врага
        'protection': 3,  # Защита врага
        'attack': 5  # Сила атаки врага
    }

    print_text("<br>=== BATTLE INITIATED ===")
    print_text(f"You are now engaging {enemy['name']} in battle! Use your weapons wisely.")
    print_text(f"{enemy['name']} has {enemy['health']} health and {enemy['protection']} protection.")
    print_text("Your ship is equipped with the following loadout:")
    for weapon in loadout:
        print_text(f"- {weapon['name']} (Strength: {weapon['strength']})")

    # Переходим к циклу боя
    battle_cycle(enemy)

# Функция для обработки боя
# Функция для обработки боя
def battle_cycle(enemy):
    # Здоровье корабля игрока
    player_health = 30

    def player_attack():
        nonlocal enemy
        total_damage = sum(weapon['strength'] for weapon in loadout)
        damage_dealt = max(0, total_damage - enemy['protection'])  # Урон с учётом защиты врага
        enemy['health'] -= damage_dealt
        print_text(f"<br>You dealt {damage_dealt} damage to {enemy['name']}. {enemy['name']} has {enemy['health']} health remaining.")

        if enemy['health'] <= 0:
            print_text(f"Congratulations! You defeated {enemy['name']}! You win the battle!")
            end_game("Player")  # Победа, игра завершена
            return  # Завершить бой

        enemy_attack()  # Враг атакует, если ещё жив

    def enemy_attack():
        nonlocal player_health
        damage_dealt = max(0, enemy['attack'] - ship_stats['protection'])  # Урон с учётом защиты игрока
        player_health -= damage_dealt
        print_text(f"{enemy['name']} dealt {damage_dealt} damage to your ship. Your ship has {player_health} health remaining.")

        if player_health <= 0:
            print_text("Your ship was destroyed. Game Over.")
            end_game("Enemy")  # Проигрыш, игра завершена
            return  # Завершить бой

        # Продолжаем цикл боя
        player_attack()

    # Начинаем с атаки игрока
    player_attack()
# Функция для завершения игры
def end_game(winner):
    if winner == "Player":
        print_text("<br><strong>You are victorious! The enemy ship has been destroyed. You win!</strong>")
    elif winner == "Enemy":
        print_text("<br><strong>The enemy has won. Your ship has been destroyed. Game over.</strong>")

# Запуск игры
game_intro()
