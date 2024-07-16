import time
from download import downloadinterface
from reco import getmy

def checktime():
    current_time = time.strftime("%H:%M:%S")
    hour = int(time.strftime("%H"))

    if 5 <= hour < 11:
        state = "morning"
    elif 11 <= hour < 15:
        state = "afternoon"
    elif 15 <= hour < 18:
        state = "evening"
    else:
        state = "night"
    return state

def main():
    
    state = checktime()
    print(f"Good {state} User!")
    print("1. Get songs Recomendation")
    print("2. Download Songs")
    
    choice = input("> ")

    if choice == '1':
        getmy()
    if choice == '2':
        downloadinterface()
    if choice == '3':
        exit("Thank you!")


if __name__ == "__main__":
    main()