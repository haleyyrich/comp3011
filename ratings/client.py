import requests
import re

BASE_URL = "http://127.0.0.1:8000/"

# get_headers will return headers w authorization if logged in
def get_headers():
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

# user registration - register command
def register():
    print("\n--- Register ---")
    username = input("Enter a username: ")

    # validate that the user entered an email address
    while True:
        email = input("Enter your email address: ")
        if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            break
        else:
            print("Please enter a valid email.")

    # validate that the user has entered a password of at least 6 characters
    while True:        
        password = input("Enter a password: ")
        if len(password) >= 6:
            break
        else:
            print("Password must be at least 6 characters long.")

    response = requests.post(f"{BASE_URL}register/", json={
    "username": username,
    "email": email,
    "password": password
    })

    print(response.json())

# user login - login command
def login():
    global TOKEN
    print("\n--- Login ---")
    username = input("Username: ")
    password = input("Password: ")

    response = requests.post(f"{BASE_URL}token/", json={"username": username, "password": password})
    
    # login successful
    if response.status_code == 200:
        data = response.json()
        TOKEN = data["access"]
        print("Login successful!")
    # login unsuccessful
    else:
        print("Login unsuccessful. Have you registered?")


TOKEN = None
# user logout - logout command
def logout():
    global TOKEN
    
    # error handling if someone tries to logout w/o being logged in
    if TOKEN is None:
        print("You are not logged in.")
        return
    
    # parsing if user is already logged in
    response = requests.post(
        f"{BASE_URL}logout/",
        headers=get_headers()
    )

    # clear token on successful log out
    if response.status_code == 200:
        print("Successfully logged out!")
        TOKEN = None
    else:
        print("Error logging out. Try again.")

# list all professors - option 1 - list command
def list():
    response = requests.get(f"{BASE_URL}list/")
    try:
        data = response.json()
        if not data:
            print("No professors found.")
            return
        
        print("\n--- Professors List ---")
        for professor in data:
            print(f"- {professor['name']} (Professor ID: {professor['id']})")
            if professor["modules"]:
                print("  Modules:")
                for module in professor["modules"]:
                    print(f"    - {module['name']} (Module ID: {module['id']}, Year: {module['year']}, Semester: {module['semester']})")
                print("-" * 50)
            else:
                print("Modules: No modules assigned")
            print()

    except requests.exceptions.JSONDecodeError:
        print("Error: Invalid")
        

# view all ratings - option 2 - view command
def view():
    response = requests.get(f"{BASE_URL}view/")
    data = response.json()
    if not data:
        print("No ratings found.")
        return
    
    print("\n--- View Ratings ---")
    for rating in data:
        professor = rating['professor']
        print(f"Professor: {professor['name']} (ID: {professor['id']})")
        module = rating['module']
        print(f"    - Module: {module['name']} (Module ID: {module['id']}, Year: {module['year']}, Semester: {module['semester']})")  
        print(f"        - Rating: {rating['rating']}")
        print(f"        - Comment: {rating['comment']}")
        print(f"        - Date: {rating['date']}")
        print("-" * 50)
    print()

    #response = requests.get(f"{BASE_URL}view/")
    #print(response.json())

# view average rating for a professor in a module - option 3 - average command
def average():
    print("\n--- Find Average Rating ---")
    professor = input("Enter professor ID: ")
    module = input("Enter module ID: ")

    response = requests.get(f"{BASE_URL}average/", params={"professor": professor, "module": module})
    
    try:
        data = response.json()
        # successfully found rating
        if response.status_code == 200:
            print(f"The average rating for that professor is {data['average_rating']} stars.")

        # various bits of error handling
        elif response.status_code == 400:
            print(f"Error: {data.get('error', 'Invalid request.')}")
        elif response.status_code == 404:
            print("No ratings found for this professor in this module.")
        else:
            print(f"Unexpected error: {data}")

    except requests.exceptions.JSONDecodeError:
        print("Unexpected response from server.")

# rate a professor - option 4 - rate command
TOKEN = None
def rate():
    global TOKEN
    if TOKEN is None:
        print("Please log on to rate a professor.")
        return

    print("\n--- Rate a Professor ---")

    # loop professor and module input until correct pair is inputted by user
    while True: 
        professor = input("Enter professor ID: ")
        module = input("Enter module ID: ")

        response = requests.post(
            f"{BASE_URL}rate/",
            json={"professor": professor, "module": module, "rating": 3, "comment": "Temporary check"},
            headers=get_headers()
        )

        try:
            response_data = response.json()

            # error handling: if incorrect pair is inputted
            if response.status_code == 400:
                error_message = response_data.get("error", "")
                if "does not teach" in error_message.lower():
                    print("The professor you have chosen does not teach this module. Please try again.")
                    continue
                # loops back until correct
                # error handling: other errors
                else:
                    print(f"Error: {error_message}")
                    return 
                
            # correct professor-module pair inputted
            elif response.status_code == 201:
                break 
            
            # another layer of error handling
            else:
                print("Unexpected error. Try again later.")
                return 

        except requests.exceptions.JSONDecodeError:
            print("The professor you have chosen does not teach this module. Please try again.")
            continue

    # loop until user inputs a rating value between 1-5
    while True:
        try:
            rating = int(input("Enter your rating (1-5): "))
            if 1 <= rating <= 5:
                break
            else:
                print("Rating must be between 1 and 5.")
        except ValueError:
            print("Please enter a number between 1 and 5.")

    comment = input("Leave a comment (optional): ")

    response = requests.post(
        f"{BASE_URL}rate/",
        json={"professor": professor, "module": module, "rating": rating, "comment": comment},
        headers=get_headers()
    )

    # more error handling because the rating function causes lots of errors
    try:
        response_data = response.json()
        if response.status_code == 201:
            print("Rating submitted successfully!")
        else:
            print(f"Error submitting rating: {response_data.get('error', 'Unknown error occurred.')}")
    
    except requests.exceptions.JSONDecodeError:
        print("Unexpected response from server.")



COMMANDS = {
    "register": register,
    "login": login,
    "logout": logout,
    "list": list,
    "view": view,
    "average": average,
    "rate": rate,
}

# CLI loop
def main():
    while True:
        command = input("Enter a command (register, login, logout, list, view, average, rate, quit): ").strip()

        if command == "quit":
            break
        elif command in COMMANDS:
            COMMANDS[command]()
        else:
            print("Not a valid command.")

if __name__ == "__main__":
    main()