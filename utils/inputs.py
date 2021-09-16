def num_input():
    try:
        usr_input = input()
        usr_input = int(usr_input)
    except ValueError:
        print("That is not a number. \nPlease enter a Number.")
        return None
    except KeyboardInterrupt:
        print("Wrong input")
        return None
    return usr_input