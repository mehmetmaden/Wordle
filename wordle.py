
import random
from colorama import Fore, Style, init
import sqlite3
from datetime import datetime

#Check the current date 
current_date = datetime.now()
current_date_str = current_date.strftime("%Y-%m-%d")

# Build db connection
db = "wordle.db"
connection = sqlite3.connect(db)

# Create a cursor 
cursor = connection.cursor()

# Start the Colorama
init(autoreset=True)

target_word_id = 0
id_in_game = 0
is_it_test = 0

# Create user with parameters and commit the cahanges
def create_user():
    global id_in_game , is_it_test
    is_it_test = 0
    #Receiving necessary inputs
    name = input("Enter your name: ").lower()
    surname = input("Enter your surname: ").lower()
    nationality = input("Enter your nationality: ").lower()
    
    #Query to add the user and commit.
    cursor.execute("INSERT INTO USERS (name,surname,nationality,played_games,games_won,daily_status) VALUES (?,?,?,?,?,?)" , (name,surname,nationality,0,0,0))

    connection.commit()

    #id of the last user added
    cursor.execute("SELECT id FROM USERS ORDER BY id DESC LIMIT 1")

    id = cursor.fetchone()[0]
    id_in_game = id

    print('Your id : -', id , '-Please note it your ip. You login with this id.')

    choose_word()


#Function to check if the player has played on the corresponding day
def check_daily_status():
    global id_in_game
    cursor.execute("SELECT daily_status FROM USERS WHERE id=?" , (id_in_game,))
    daily_status = cursor.fetchone()[0]

    if daily_status == 0:
        return True
    else:
        return False


# Login function
def login():
    global id_in_game , is_it_test
    #If the user entered the login method, it is not a test, so we update the variable to 0
    is_it_test = 0
    while True:
        id = input("Enter your id : ")

        try:
            #Check id if int
            id = int(id)
        except:
            print("Invalid id format. Enter again.")
            continue
        
        try:
            #We get the entered id user.
            cursor.execute("SELECT * FROM USERS WHERE id=?", (id,))
            object = cursor.fetchone()
            
            if (object):
                print('Welcome back ' ,object[1])
                id_in_game = id

                #We pull the user's log status and start the game if they haven't played.
                if check_daily_status():
                    choose_word()
                else:
                    print("You already played today. Please wait tomorrow.")
                    break
                break
            else:
                print("Invalid id. Enter again")
                continue
        
        except sqlite3.Error as error_db:
            print("Database error:", error_db)
            print("Try again.")
            continue
    

#Test function
def test():
    global is_it_test
    #Update the test variable with 1.
    is_it_test = 1

    while True:
        #We ask the user if they want a random word or if they want their own word.
        choose = input("Select the word you want to test. If you want it to be random, leave it blank and just press enter.  ")
        
        try:
            choose = str(choose)
        
        except:
            print("A word can only contain letters. Please try again.")
            continue
        
        #Checking whether the word entered by the user exists in the database
        cursor.execute("SELECT * FROM WORDS WHERE word=?", (choose,))
        is_it = cursor.fetchone()

        try:
            #If the word is empty, a random word is selected.
            if choose == '':
                choose_word()
                break
            
            #If the selected word is in the database, the game is started with the selected word.
            elif bool(is_it):
                target_word = choose
                play_wordle(target_word)
                break
            
            #If the selected word is not in the database, a new word is requested.
            else:
                print("The word is not in the database. Enter a with 5 letter different word.")
                continue
            
        except sqlite3.Error as error_db:
            print("Database error:", error_db)
            print("Try again.")
            continue


#Word selection function
def choose_word():
    global target_word_id
    #We use it to check whether the Games table is full or empty.
    cursor.execute("SELECT COUNT(*) FROM GAMES;")
    is_empty = cursor.fetchone()[0]
    
    #If the games table is empty, we assign the last date as 0.
    if is_empty == 0:
        last_date = '0'
    #In the Games table we get the date of the last game played.
    else:
        cursor.execute("SELECT date FROM games ORDER BY id DESC LIMIT 1")
        last_date = cursor.fetchone()[0]

    #If the date of the last game is the same as the current day, the game is started with the word of the last game.
    if last_date == current_date_str:
        cursor.execute("SELECT w.* FROM WORDS w JOIN GAMES g ON w.id = g.word_id ORDER BY g.id DESC LIMIT 1;")

        target_word_object = cursor.fetchone()
        target_word = target_word_object[1]
        target_word_id = target_word_object[0]
        play_wordle(target_word)

    #In the other case, since the days are not the same, a new word is randomly selected from the Words table.
    else:
        cursor.execute("SELECT id FROM WORDS ORDER BY id DESC LIMIT 1")
        word_count = cursor.fetchone()[0]
        random_id = random.randint(1, word_count)
        target_word_id = random_id
        cursor.execute("SELECT word FROM WORDS WHERE id=?", (random_id,))
        target_word = cursor.fetchone()[0]
        play_wordle(target_word)


#Check function that compares the letters of the predicted word with the letters of the word to be found
def evaluate_guess(target_word, guessed_word):

    feedback = ""
    for i in range(len(target_word)):
        if guessed_word[i] == target_word[i]:
            feedback += Fore.GREEN + guessed_word[i] + Style.RESET_ALL
        elif guessed_word[i] in target_word:
            feedback += Fore.YELLOW + guessed_word[i] + Style.RESET_ALL
        else:
            feedback += Fore.BLACK + guessed_word[i] + Style.RESET_ALL
    return feedback


#Function that plays the game
def play_wordle(target_word):
    max_attempts = 6 #Number of rights
    attempts = 0 #Number of trials of the user
    global target_word_id, id_in_game , is_it_test

    print("Welcome to Wordle!")
    print("Try to guess the word.")
    print(target_word)

    #Loop to check if the user's number of attempts is less than max attempts
    while attempts < max_attempts:
        guess = input("Enter your guess: ").lower()#Take input from the user

        #Function to check if the received word has 5 letters.
        if len(guess) == 5:
            
            #Since the received word must be a real word, check whether it exists in the database or not.
            cursor.execute("SELECT * FROM WORDS WHERE word=?", (guess,))
            is_it = cursor.fetchone()

            if bool(is_it):            
                
                #When the word received is equal to the word to be known
                if guess == target_word:
                    print(Fore.GREEN + "Congratulations! You guessed the word:", 
                     Fore.GREEN +target_word + Style.RESET_ALL)
                    
                    #Control to update the tables if the game being played is not a test.
                    if is_it_test == 0:
                        #Update words table
                        cursor.execute("UPDATE WORDS SET game_count =   game_count+1 , success_count = success_count+1 WHERE  word=?" , (target_word,))

                        #Update games table
                        cursor.execute("INSERT INTO GAMES(date,word_id, user_id,status) VALUES (?,?,?,?)" , (current_date_str,   target_word_id,id_in_game,1))

                        #Update users table
                        cursor.execute("UPDATE USERS SET played_games =     played_games+1 , games_won = games_won+1 ,  daily_status = 1 WHERE id=?" , (id_in_game,))

                        connection.commit()

                    break
                # Code block that checks the letter and gives feedback if the received word is not equal to the word to be known.
                else:
                    feedback = evaluate_guess(target_word, guess)
                    print(Fore.BLUE + "-----------------------" + Style.RESET_ALL)
                    print("Feedback:", feedback)
                    print("You have ", max_attempts-attempts-1 ,"left")
                    print(Fore.BLUE + "-----------------------" + Style.RESET_ALL)  
                    attempts += 1
            # Code block that allows us to request a new word if the received word is not in the database.
            else:
                print(Fore.LIGHTBLUE_EX + "-----------------------" + Style.RESET_ALL)
                print("Please enter a real word.")
                print("You have ", max_attempts-attempts ," left")
                print(Fore.LIGHTBLUE_EX + "-----------------------" + Style.RESET_ALL)
        #Code block that allows us to request a new word if the received word does not have 5 letters
        else:
            print(Fore.LIGHTBLUE_EX + "-----------------------" + Style.RESET_ALL)
            print("Your word need to be 5 letter.")
            print("You have ", max_attempts-attempts ," left")
            print(Fore.LIGHTBLUE_EX + "-----------------------" + Style.RESET_ALL)

    #Code block to run when the piper's right is up
    if attempts == max_attempts:
        print(Fore.LIGHTYELLOW_EX + "-----------------------" + Style.RESET_ALL)
        print(Fore.RED + "Sorry, you're out of attempts. The correct word was:", Fore.GREEN + target_word + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + "-----------------------" + Style.RESET_ALL)

        #Block of code to update the tables if it is not a test because it lost the game.
        if is_it_test == 0:
            #Update words table
            cursor.execute("UPDATE WORDS SET game_count = game_count+1  WHERE   word=?" , (target_word,))

            #Update games table
            cursor.execute("INSERT INTO GAMES(date,word_id,user_id,status)  VALUES (?,?,?,?)" , (current_date_str,target_word_id,id_in_game, 0))

            #Update users table
            cursor.execute("UPDATE USERS SET played_games = played_games+1 ,    daily_status = 1 WHERE id=?" , (id_in_game,))

            connection.commit()


# This function runs when the game first starts and checks the day. If the day the game is started is not the same as the day the last game was played, it resets the daily_status variable for all users and lets them play on that day. If the day has not changed, it does nothing.
def check_the_day():
    #First we check if the game has been played before. If not, we call the main function without doing anything.
    cursor.execute("SELECT COUNT(*) FROM GAMES;")
    is_empty = cursor.fetchone()[0]
    if is_empty == 0:
        main()
    else:
        #We get the date of the last game played.
        cursor.execute("SELECT date FROM games ORDER BY id DESC LIMIT 1")
        last_date = cursor.fetchone()[0]


        if last_date != current_date_str:
            #Users' daily_status is updated if the date of the last game and the date of the day played are not equal.
            cursor.execute("UPDATE USERS SET daily_status = 0;")
            connection.commit()
            main()
        else:
            #If it is equal, we call the main function without doing anything.
            main()


#Function where the user chooses which statistic they want to see.
def statistics():
    while True:
        dec = input("1. What is the success rate of “user?”.\n"
                    "2. Which words did “user” failed?.\n"
                    "3. Which words did “user” succeeded?\n"
                    "4. How many users succeeded word “word”?\n"
                    "5. Which words score more successes?\n"
                    "6. Which words score more failures?\n"
                    "7. Most played word?\n"
                    "0. Main Menu\n")

        dec = int(dec)

        if dec == 1:
            success_rate()
        elif dec == 2:
            failed_words_w_user()
        elif dec == 3:
            succeeded_words_w_user()
        elif dec == 4:
            count_success_word()
        elif dec == 5:
            more_succeeded_word()
        elif dec == 6:
            more_failed_word()
        elif dec ==7:
            most_played()
        elif dec == 0:
            break
        else:
            print("Try again.")
            continue
    

#Function where the user will see the success rate of the player whose id is entered.
def success_rate():
    while True:
        id = input("Enter the id of the user you want to review. ")

        try:
            id = int(id)
        except:
            print("Invalid id format. Enter again.")
            continue

        try:
            #Check if the id received from the user is in the database.
            cursor.execute("SELECT * FROM USERS WHERE id=?", (id,))
            object = cursor.fetchone()
            
            if (object):
                #We print the name if it exists and calculate and print the proportion of that person.
                print('Welcome  ' , object[1] ,' ',object[2])
                
                rate = (object[5]/object[4]) * 100
                print("Success rate of",object[1] , object[2],
                    "with",object[0],"id is : %",rate,"\n")
                break
            else:
                print("Invalid id. Enter again")
                continue
        
        except sqlite3.Error as error_db:
            print("Database error:", error_db)
            print("Try again.")
            continue


#Function that shows which words a user has got wrong.
def failed_words_w_user():
    while True:
        id = input("Enter the id of the user you want to review. ")

        try:
            id = int(id)
        except:
            print("Invalid id format. Enter again.")
            continue

        try:
            #Function that returns the words that the entered user got wrong.
            cursor.execute("SELECT w.word FROM games g JOIN words w ON g.word_id = w.id WHERE g.user_id = ? AND g.status = 0;", (id,))
            object = cursor.fetchall()
            
            #Function that returns which user the entered id belongs to.
            cursor.execute("SELECT * FROM USERS WHERE id=?", (id,))
            object_user = cursor.fetchone()
            
            if (object and object_user):
                #Block of code that, if two functions return values, prints the tuple from the function that returns the words in order.
                print("Games lost by a user with id", id ,"named",object_user[1],object_user[2],".")
                i=1
                for tup in object:
                    
                    word = tup[0]
                    print(i,'. word',word)
                    i += 1
                print("\n\n")
                break
            elif (not object and object_user):
                #Function to run if there is a user but the function returning unknown words does not return a value
                print("This user has no lost games.\n")
                break
            else:
                #Code indicating that there will be no such user in the last case.
                print("Invalid id. Enter again")
                continue
        
        except sqlite3.Error as error_db:
            print("Database error:", error_db)
            print("Try again.")
            continue


#Function that shows which words a user got right.
def succeeded_words_w_user():
    while True:
        id = input("Enter the id of the user you want to review. ")

        try:
            id = int(id)
        except:
            print("Invalid id format. Enter again.")
            continue

        try:
            #Function that returns the words that the entered user made correct.
            cursor.execute("SELECT w.word FROM games g JOIN words w ON g.word_id = w.id WHERE g.user_id = ? AND g.status = 1;", (id,))
            object = cursor.fetchall()
            
            #Function that returns which user the entered id belongs to.
            cursor.execute("SELECT * FROM USERS WHERE id=?", (id,))
            object_user = cursor.fetchone()
            
            if (object and object_user):
                #Block of code that, if two functions return values, prints the tuple from the function that returns the words in order.
                print("Games won by a user with id", id ,"named",object_user[1],object_user[2],".")
                i=1
                for tup in object:
                    
                    word = tup[0]
                    print(i,'. word',word)
                    i += 1
                print("\n\n")
                break
            elif (not object and object_user):
                #Function to run if there is a user but the function returning known words does not return a value
                print("This user has no won games.\n")
                break
            else:
                #Code indicating that there will be no such user in the last case.
                print("Invalid id. Enter again")
                continue
        
        except sqlite3.Error as error_db:
            print("Database error:", error_db)
            print("Try again.")
            continue


#Function that shows how many times the word entered by the user is known.
def count_success_word():
    while True:
        word = input("Enter the word you want to review. ")

        try:
            word = str(word)
        except:
            print("Invalid word format. Enter again.")
            continue

        try:
            #Checking whether the word received from the user exists in the database.
            cursor.execute("SELECT * FROM WORDS WHERE word=?", (word,))
            object = cursor.fetchone()
            
            if (object):
                #Function that will run if the word is in the database.
                if(object[2] == 0):
                    #Code indicating that the word has not been played before if the number of times the word has been played is 0.
                    print("The word", word ,"has never been played before.")
                else:
                    #Function that shows how many times the word has been played and how many times it is known.
                    print("The word", word ,"was played", object[2] ,"times and known", object[3] ,"times.")
                break
            else:
                print("Invalid word. Enter again.")
                continue
        
        except sqlite3.Error as error_db:
            print("Database error:", error_db)
            print("Try again.")
            continue


#Function showing the most known word.
def more_succeeded_word():
    cursor.execute("SELECT * from words ORDER BY success_count DESC LIMIT 1;")
    object = cursor.fetchone()
    print("The word with the highest number of known words is",object[1],".", object[2],"times played and",object[3],"times known.")


#Function showing the most unknown word.
def more_failed_word():
    cursor.execute("SELECT * from words ORDER BY game_count-success_count DESC LIMIT 1;")
    object = cursor.fetchone()
    print("The word with the highest number of not known words is",object[1],".", object[2],"times played and",object[3],"times known.")


#Function showing the most played word.
def most_played():
    cursor.execute("SELECT * from words ORDER BY game_count DESC LIMIT 1")
    object = cursor.fetchone()

    print("Most played word is '",object[1],"'. With",object[2],"game. This has been known",object[3],"times.")


#The main function where the user selects the state they want to be in when they enter the game.
def main():
    while True:
        dec = input("1. Create User\n2. Login\n3. Statistics\n4. Test \n0. Exit\n")

        dec = int(dec)

        if dec == 1:
            create_user()
        elif dec == 2:
            login()
        elif dec == 3:
            statistics()
        elif dec == 4:
            test()
        elif dec == 0:
            connection.close()
            break
        else:
            print("Try again.")
            continue



if __name__ == "__main__":
    check_the_day()