import random

print("🎲 Welcome to the Number Guessing Game!")
number = random.randint(1, 10)
guess = int(input("Guess a number between 1 and 10: "))

if guess == number:
    print(f"🎉 Amazing! You guessed it right. The number was {number}.")
else:
    print(f"❌ Sorry, the number was {number}. Better luck next time!")