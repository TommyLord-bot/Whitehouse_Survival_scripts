import pickle  # For serialization of the players list


# Function to calculate the total power of a lane (Only top 20 count)
def total_power(lane):
    # Since lanes are sorted, we just take the first 20
    return sum(player[1] for player in lane[:20])


# Redistribute players to balance power between lanes 1 and 3
def redistribute_players(lanes):
    players_list = [player for lane in lanes for player in lane]
    sorted_players = sorted(players_list, key=lambda x: x[1], reverse=True)
    new_lanes = [[], [], []]

    for player in sorted_players:
        # Balancing logic based on the top-20 power rule
        if len(new_lanes[0]) < 20 and total_power(new_lanes[0]) <= total_power(new_lanes[2]):
            new_lanes[0].append(player)
        elif len(new_lanes[2]) < 20:
            new_lanes[2].append(player)
        else:
            new_lanes[1].append(player)

    # Sort each lane by power descending after redistribution
    for lane in new_lanes:
        lane.sort(key=lambda x: x[1], reverse=True)

    return new_lanes


# Function to find players by partial name
def find_players_by_partial_name(partial_name, players):
    return [name for name in players.keys() if partial_name.lower() in name.lower()]


# Function to fill a lane with players
def fill_lane(players, lanes):
    try:
        lane_number = int(input("Enter lane number to fill (1, 2, or 3): "))
        if lane_number not in [1, 2, 3]:
            print("Invalid lane number. Please choose between 1, 2, or 3.")
            return

        while True:
            partial_name = input("Enter player name (or 'done' to finish): ")
            if partial_name.lower() == 'done':
                break

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
                        full_name = input("Enter full name to add: ")
                    elif add_new_player == '2':
                        continue
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                        continue
                else:
                    print("Invalid choice. Please enter 1 or 2.")
                    continue

                power = int(input("Enter player power: "))
                lane = lane_number
                players[full_name] = (power, lane)
                lanes[lane - 1].append((full_name, power, lane))

            elif len(matching_names) == 1:
                found_name = matching_names[0]
                print(f"Found player '{found_name}'.")

                power_input = int(
                    input(f"Enter power for '{found_name}' (or -1 to add '{partial_name}' as a new player): "))

                if power_input == -1:
                    full_name = partial_name
                    power = int(input(f"Enter power for NEW player '{full_name}': "))
                else:
                    full_name = found_name
                    power = power_input

                lane = lane_number
                players[full_name] = (power, lane)
                lanes[lane - 1].append((full_name, power, lane))

            else:
                print("Multiple players found:")
                for i, name in enumerate(matching_names, start=1):
                    print(f"{i}. {name}")
                choice = int(input("Enter the number of the player you want to use (or 0 to add a new player): "))

                if choice == 0:
                    full_name = partial_name
                    power = int(input(f"Enter power for NEW player '{full_name}': "))
                elif 1 <= choice <= len(matching_names):
                    full_name = matching_names[choice - 1]
                    power = int(input(f"Enter power for player '{full_name}': "))
                else:
                    print("Invalid choice. Please try again.")
                    continue

                lane = lane_number
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
            new_name = input(f"Enter new name for player '{old_name}': ")
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
                new_name = input(f"Enter new name for player '{old_name}': ")
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

            new_power = int(input(f"Enter new power for {target_name}: "))
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
    with open("players.dat", "wb") as file:
        pickle.dump(players, file)
    print("Player list saved successfully.")


# Function to load the players list from a file
def load_players():
    try:
        with open("players.dat", "rb") as file:
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

        print("Player list loaded successfully.")
        return unique_players

    except FileNotFoundError:
        print("No existing player data found.")
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
    players = load_players()  # Load players from file at start
    lanes = [[] for _ in range(3)]
    reserves = []

    # Distribute players into initial lanes
    for player, (power, lane) in players.items():
        if 1 <= lane <= 3:
            lanes[lane - 1].append((player, power, lane))

    for lane in lanes:
        lane.sort(key=lambda x: x[1], reverse=True)

    while True:
        display_menu()
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
            print("\nPlayer Counts:")
            for i, lane in enumerate(lanes):
                print(f"Lane {i + 1}: {len(lane)} players")
        elif choice == "6":
            lanes = [[] for _ in range(3)]
            for name in players:
                p_power, p_lane = players[name]
                players[name] = (p_power, 0)
            print("Lanes cleared. Player data preserved.")
        elif choice == "7":
            save_players(players)
        elif choice == "8":
            players = load_players()
            lanes = [[] for _ in range(3)]
            for player, (power, lane) in players.items():
                if 1 <= lane <= 3:
                    lanes[lane - 1].append((player, power, lane))
            for lane in lanes:
                lane.sort(key=lambda x: x[1], reverse=True)
        elif choice == "9":
            print("\nCurrent Lane Assignments (Top 20 Power counted):")
            for i, lane in enumerate(lanes):
                pwr = total_power(lane)
                count = len(lane)
                print(f"Lane {i + 1}: {[(p[0], p[1]) for p in lane]} | Count: {count} | Top 20 Power: {pwr}")
        elif choice == "10":
            new_lanes = redistribute_players(lanes)
            for i, lane in enumerate(new_lanes):
                pwr = total_power(lane)
                print(f"Lane {i + 1}: {[(p[0], p[1]) for p in lane]} | Top 20 Power: {pwr}")
        elif choice == "11":
            print("Exiting program.")
            save_players(players)
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 11.")


if __name__ == "__main__":
    main()