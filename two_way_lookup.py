user_directory = {
    "j_miller": "UID-1042", 
    "a_chen": "UID-5581",
    "d_water":"UID-1230"
}
id_dir = {
    badge_id: username for username,
#   |------------------------------| 
#           1. New Blueprint  
    badge_id in user_directory.items()
#   |--------------------------------|
#            2. Loop Engine
}
# The longhand way:
#id_dir = {}
#for username, badge_id in user_directory.items():
#    id_dir[badge_id] = username

print('--- Two Way Access Directory ---')
print('1. Lookup Badge ID by Username')
print('2. Lookup Username by BadgeID')
print('3. Exit')

user_requestor = input('Who are you? : ')

while True:



    choice= int(input(f"hello {user_requestor}, please choose from the above options: "))

    if choice == 1:
        username = input(f'What is the user\'s username: ').strip().lower()
        badge_id = user_directory.get(username)

        if badge_id:
            print(f"[FOUND]  {username} is assigned to  {badge_id}")
        else:
            print(f"Username invalid or not found")

    elif choice == 2:
        badge_id = input(' Enter Badge ID (e.g., UID-####): ').strip().upper()
        username = id_dir.get(badge_id)

        if username: 
            print(f"[FOUND] Badge id {badge_id} -> Assigned to {username}")
        else:
            print(f"Badge ID invalid or not found")

    elif choice == 3:
        print ('Exiting directory. Bye!')
        break  

    else:
        print(f'Invalid entry, please choose 1., 2., or 3')