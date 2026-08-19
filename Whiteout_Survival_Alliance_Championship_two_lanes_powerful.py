import os
import pickle  # For serialization of the players list


DEFAULT_PLAYER_FILE = "players.dat"
CURRENT_PLAYER_FILE = DEFAULT_PLAYER_FILE


def list_player_data_files():
    return sorted(
        [
            name for name in os.listdir(".")
            if os.path.isfile(name) and name.lower().endswith(".dat")
        ]
    )


def normalize_player_file_name(file_name):
    normalized = file_name.strip()
    if "" == normalized:
        normalized = DEFAULT_PLAYER_FILE
    if not normalized.lower().endswith(".dat"):
        normalized += ".dat"
    return normalized


def choose_player_data_file():
    while True:
        available_files = list_player_data_files()

        print("\n--- Player Data Files ---")
        if 0 == len(available_files):
            print("No .dat files found in current folder.")
        else:
            for i, file_name in enumerate(available_files, start=1):
                print(f"{i}. {file_name}")

        print("N. Create or choose by new file name")
        choice = input("Select file number or N: ").strip()

        if choice.lower() == "n":
            new_file = input("Enter player file name (blank for players.dat): ")
            selected_file = normalize_player_file_name(new_file)
            print(f"Selected player file: {selected_file}")
            return selected_file

        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(available_files):
                selected_file = available_files[index - 1]
                print(f"Selected player file: {selected_file}")
                return selected_file

        print("Invalid choice. Please try again.")


# Function to calculate the total power of a lane (Only top 20 count)
def total_power(lane):
    # Since lanes are sorted, we just take the first 20
    return sum(player[1] for player in lane[:20])


# Redistribute players to balance power between lanes 1 and 3
def redistribute_players(lanes, mode="2-1-2"):
    players_list = [player for lane in lanes for player in lane]
    sorted_players = sorted(players_list, key=lambda x: x[1], reverse=True)
    new_lanes = [[], [], []]

    for player in sorted_players:
        # player structure is (name, power, original_lane)
        if mode == "1-1-1":
            target_lane = min(range(3), key=lambda i: total_power(new_lanes[i]))
            new_lanes[target_lane].append(player)
        else:
            if len(new_lanes[0]) < 20 and total_power(new_lanes[0]) <= total_power(new_lanes[2]):
                new_lanes[0].append(player)
            elif len(new_lanes[2]) < 20:
                new_lanes[2].append(player)
            else:
                new_lanes[1].append(player)

    for lane in new_lanes:
        lane.sort(key=lambda x: x[1], reverse=True)

    return new_lanes


# Function to find players by partial name
def find_players_by_partial_name(partial_name, players):
    return [name for name in players.keys() if partial_name.lower() in name.lower()]


def read_non_negative_power(prompt):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer power.")
            continue

        if value < 0:
            print("Error: power cannot be negative. Returning to the main menu.")
            return None

        return value


def read_player_name(prompt):
    while True:
        name = input(prompt).strip()
        if "" == name:
            print("Error: player name cannot be blank. Returning to the main menu.")
            return None
        return name


# Function to fill a lane with players
def fill_lane(players, lanes):
    try:
        lane_number = int(input("Enter lane number to fill (1, 2, or 3): "))
        if lane_number not in [1, 2, 3]:
            print("Invalid lane number. Please choose between 1, 2, or 3.")
            return

        while True:
            partial_name = input("Enter player name (or 'done' to finish): ").strip()
            if partial_name.lower() == 'done':
                break
            if "" == partial_name:
                print("Error: player name cannot be blank. Returning to the main menu.")
                return

            matching_names = find_players_by_partial_name(partial_name, players)

            if len(matching_names) == 0:
                print(f"No players found with partial name '{partial_name}'.")
                add_new_player = input(
                    f"Do you want to add '{partial_name}' as a new player? (1 for yes, 2 for no): ")
                if add_new_player == '1':
                    full_name = partial_name
                elif add_new_player == '2':
                    change_partial_name = input(
                        f"Change name for '{partial_name}', or quit adding this player? (1 for yes, 2 for no): ")
                    if change_partial_name == '1':
                        full_name = read_player_name("Enter full name to add: ")
                        if full_name is None:
                            return
                    elif add_new_player == '2':
                        continue
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                        continue
                else:
                    print("Invalid choice. Please enter 1 or 2.")
                    continue

                power = read_non_negative_power("Enter player power: ")
                if power is None:
                    return
                lane = lane_number
                players[full_name] = (power, lane)
                lanes[lane - 1].append((full_name, power, lane))

            elif len(matching_names) == 1:
                found_name = matching_names[0]
                print(f"Found player '{found_name}'.")

                power_input = input(
                    f"Enter power for '{found_name}' (or -1 to add '{partial_name}' as a new player): ")
                try:
                    power_value = int(power_input)
                except ValueError:
                    print("Invalid input. Please enter a valid integer power.")
                    continue

                if power_value < -1:
                    print("Error: power cannot be negative. Returning to the main menu.")
                    return

                if power_value == -1:
                    while True:
                        choice = input(
                            f"Use '{partial_name}' as the NEW player name (1) or enter a different full name (2)? ")
                        if choice == '1':
                            full_name = partial_name
                            break
                        if choice == '2':
                            full_name = read_player_name(
                                f"Enter the full name for the NEW player (instead of '{partial_name}'): ")
                            if full_name is None:
                                return
                            break
                        print("Invalid choice. Please enter 1 to use the partial name or 2 to enter a new full name.")

                    power = read_non_negative_power(f"Enter power for NEW player '{full_name}': ")
                    if power is None:
                        return
                else:
                    full_name = found_name
                    power = power_value
                    if power < 0:
                        print("Error: power cannot be negative. Returning to the main menu.")
                        return

                lane = lane_number
                if full_name in players:
                    old_power, old_lane = players[full_name]
                    if 1 <= old_lane <= 3:
                        old_entry = (full_name, old_power, old_lane)
                        if old_entry in lanes[old_lane - 1]:
                            lanes[old_lane - 1].remove(old_entry)
                players[full_name] = (power, lane)
                lanes[lane - 1].append((full_name, power, lane))

            else:
                print("Multiple players found:")
                for i, name in enumerate(matching_names, start=1):
                    print(f"{i}. {name}")
                choice = int(input("Enter the number of the player you want to use (or 0 to add a new player): "))

                if choice == 0:
                    full_name = read_player_name(f"Enter the full name for the NEW player (instead of '{partial_name}'): ")
                    if full_name is None:
                        return
                    power = read_non_negative_power(f"Enter power for NEW player '{full_name}': ")
                    if power is None:
                        return
                elif 1 <= choice <= len(matching_names):
                    full_name = matching_names[choice - 1]
                    power = read_non_negative_power(f"Enter power for player '{full_name}': ")
                    if power is None:
                        return
                else:
                    print("Invalid choice. Please try again.")
                    continue

                lane = lane_number
                if full_name in players:
                    old_power, old_lane = players[full_name]
                    if 1 <= old_lane <= 3:
                        old_entry = (full_name, old_power, old_lane)
                        if old_entry in lanes[old_lane - 1]:
                            lanes[old_lane - 1].remove(old_entry)
                players[full_name] = (power, lane)
                lanes[lane - 1].append((full_name, power, lane))

            lanes[lane_number - 1].sort(key=lambda x: x[1], reverse=True)
            print(f"Player {full_name} added to lane {lane_number} (Sorted by power).")
            save_players(players)

    except ValueError:
        print("Invalid input. Please enter a valid number.")


# Function to change a player's name
def change_player_name(players, lanes):
    try:
        partial_name = input("Enter player name to change: ")
        matching_names = find_players_by_partial_name(partial_name, players)

        if len(matching_names) == 0:
            print(f"No players found with partial name '{partial_name}'.")
        elif len(matching_names) == 1:
            old_name = matching_names[0]
            new_name = read_player_name(f"Enter new name for player '{old_name}': ")
            if new_name is None:
                return
            power, lane = players.pop(old_name)
            players[new_name] = (power, lane)
            for idx, player in enumerate(lanes[lane - 1]):
                if player[0] == old_name:
                    lanes[lane - 1][idx] = (new_name, power, lane)
            print(f"Player '{old_name}' renamed to '{new_name}'.")
            save_players(players)
        else:
            print("Multiple players found:")
            for i, name in enumerate(matching_names, start=1):
                print(f"{i}. {name}")
            choice = int(input("Enter the number of the player whose name you want to change: "))
            if 1 <= choice <= len(matching_names):
                old_name = matching_names[choice - 1]
                new_name = read_player_name(f"Enter new name for player '{old_name}': ")
                if new_name is None:
                    return
                power, lane = players.pop(old_name)
                players[new_name] = (power, lane)
                for idx, player in enumerate(lanes[lane - 1]):
                    if player[0] == old_name:
                        lanes[lane - 1][idx] = (new_name, power, lane)
                print(f"Player '{old_name}' renamed to '{new_name}'.")
                save_players(players)
            else:
                print("Invalid choice. Please try again.")

    except ValueError:
        print("Invalid input. Please enter a valid number.")


def change_player_power(players, lanes):
    try:
        partial_name = input("Enter player name to change power: ")
        matching_names = find_players_by_partial_name(partial_name, players)

        if len(matching_names) == 0:
            print(f"No players found with partial name '{partial_name}'.")
        else:
            if len(matching_names) == 1:
                target_name = matching_names[0]
            else:
                print("Multiple players found:")
                for i, name in enumerate(matching_names, start=1):
                    print(f"{i}. {name}")
                choice = int(input("Enter the number of the player: "))
                target_name = matching_names[choice - 1]

            new_power = read_non_negative_power(f"Enter new power for {target_name}: ")
            if new_power is None:
                return
            old_power, lane = players[target_name]
            players[target_name] = (new_power, lane)

            for idx, player in enumerate(lanes[lane - 1]):
                if player[0] == target_name:
                    lanes[lane - 1][idx] = (target_name, new_power, lane)

            if 1 <= lane <= 3:
                lanes[lane - 1].sort(key=lambda x: x[1], reverse=True)

            print(f"Power for {target_name} updated to {new_power}. Lane re-sorted.")
            save_players(players)
    except (ValueError, IndexError):
        print("Invalid input.")


def remove_player(players, lanes):
    try:
        partial_name = input("Enter player name to remove: ")
        matching_names = find_players_by_partial_name(partial_name, players)

        if len(matching_names) == 0:
            print(f"No players found with partial name '{partial_name}'.")
        elif len(matching_names) == 1:
            full_name = matching_names[0]
            print(f"Found player '{full_name}'. Removing this player.")
            power, lane = players.pop(full_name)
            lanes[lane - 1].remove((full_name, power, lane))
            print(f"Player {full_name} removed.")
            save_players(players)
        else:
            print("Multiple players found:")
            for i, name in enumerate(matching_names, start=1):
                print(f"{i}. {name}")
            choice = int(input("Enter the number of the player you want to remove: "))
            if 1 <= choice <= len(matching_names):
                full_name = matching_names[choice - 1]
                print(f"Removing player '{full_name}'.")
                power, lane = players.pop(full_name)
                lanes[lane - 1].remove((full_name, power, lane))
                print(f"Player {full_name} removed.")
                save_players(players)
            else:
                print("Invalid choice. Please try again.")

    except ValueError:
        print("Invalid input. Please enter a valid number.")


# Function to save the players list to a file
def save_players(players):
    with open(CURRENT_PLAYER_FILE, "wb") as file:
        pickle.dump(players, file)
    print(f"Player list saved successfully to '{CURRENT_PLAYER_FILE}'.")


# Function to load the players list from a file
def load_players():
    try:
        with open(CURRENT_PLAYER_FILE, "rb") as file:
            players = pickle.load(file)

        # Remove duplicates from players dictionary
        seen_names = set()
        unique_players = {}

        for name, (power, lane) in players.items():
            if name not in seen_names:
                seen_names.add(name)
                unique_players[name] = (power, lane)
            else:
                print(f"Duplicate player found and removed: {name}")

        print(f"Player list loaded successfully from '{CURRENT_PLAYER_FILE}'.")
        return unique_players

    except FileNotFoundError:
        print(f"No existing player data found in '{CURRENT_PLAYER_FILE}'. Starting with empty list.")
        return {}


# Function to display the menu
def display_menu():
    print("\nMenu:")
    print("1. Fill lane")
    print("2. Remove player")
    print("3. Change player name")
    print("4. Change player power")
    print("5. Show number of players in each lane")
    print("6. Clear lanes (keep player data)")
    print("7. Save player list")
    print("8. Load player list")
    print("9. Show current lanes (Top 20 Power Cap)")
    print("10. Show lanes and total power (Redistributed/Balanced)")
    print("11. Exit")


def main():
    global CURRENT_PLAYER_FILE
    CURRENT_PLAYER_FILE = choose_player_data_file()

    players = load_players()
    lanes = [[] for _ in range(3)]
    last_redistribution = None

    for player, (power, lane) in players.items():
        if 1 <= lane <= 3:
            lanes[lane - 1].append((player, power, lane))
    for lane in lanes:
        lane.sort(key=lambda x: x[1], reverse=True)

    while True:
        print("\n--- Lane Management System ---")
        print("1. Fill lane            7. Save player list")
        print("2. Remove player        8. Load player list")
        print("3. Rename player        9. Show current lanes (Active)")
        print("4. Change power         10. Preview Balanced Redistribution")
        print("5. Player counts        11. SAVE Balanced Redistribution to File")
        print("6. Clear lanes          12. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            fill_lane(players, lanes)
        elif choice == "2":
            remove_player(players, lanes)
        elif choice == "3":
            change_player_name(players, lanes)
        elif choice == "4":
            change_player_power(players, lanes)
        elif choice == "5":
            for i, l in enumerate(lanes):
                print(f"Lane {i + 1}: {len(l)} players")
        elif choice == "6":
            lanes = [[] for _ in range(3)]
            for name in players:
                p_pwr, p_ln = players[name]
                players[name] = (p_pwr, 0)
            print("Lanes cleared.")
        elif choice == "7":
            save_players(players)
        elif choice == "8":
            players = load_players()
            lanes = [[] for _ in range(3)]
            for p, (pwr, ln) in players.items():
                if 1 <= ln <= 3: lanes[ln - 1].append((p, pwr, ln))
            for l in lanes: l.sort(key=lambda x: x[1], reverse=True)
        elif choice == "9":
            for i, l in enumerate(lanes):
                print(f"Lane {i + 1}: {[(p[0], p[1]) for p in l]} | Top 20 Pwr: {total_power(l)}")

        elif choice == "10":
            print("\nSelect Distribution Mode:\n1. Even Distribution (1-1-1)\n2. Power Lane Distribution (2-1-2)")
            mode_choice = input("Choice (1 or 2): ")
            mode_str = "1-1-1" if mode_choice == "1" else "2-1-2"
            last_redistribution = redistribute_players(lanes, mode=mode_str)
            print(f"\n--- PREVIEW: {mode_str} Redistribution ---")
            for i, l in enumerate(last_redistribution):
                display_list = [(p[0], p[1], f"({p[2]})") for p in l]
                print(f"Lane {i + 1}: {display_list} | Top 20 Pwr: {total_power(l)}")
            print("\nTo keep these changes, select Option 11.")

        elif choice == "11":
            if last_redistribution is None:
                print("Error: Please run Option 10 first.")
            else:
                for i, new_lane_data in enumerate(last_redistribution):
                    new_ln_num = i + 1
                    updated_list = []
                    for p in new_lane_data:
                        name, pwr = p[0], p[1]
                        players[name] = (pwr, new_ln_num)
                        updated_list.append((name, pwr, new_ln_num))
                    lanes[i] = updated_list
                save_players(players)
                last_redistribution = None
                print("Redistribution applied and saved successfully!")

        elif choice == "12":
            save_players(players)
            break


if __name__ == "__main__":
    main()
