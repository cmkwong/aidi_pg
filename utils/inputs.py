def num_check():
    try:
        num_input = input()
        num_input = int(num_input)
    except ValueError:
        print("That is not a number. \nPlease enter a Number.")
        return None
    except KeyboardInterrupt:
        print("Wrong input")
        return None
    return num_input

def user_confirm():
    placeholder = 'Input [y]es to confirm OR others to cancel: '
    confirm_input = input(placeholder)
    if confirm_input == 'y' or confirm_input == "yes":
        return True
    else:
        return False