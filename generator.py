# Generator to create 5 letter domains that would be readable following the cvcvc, vcvcv and cvvcc pattern

from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///domain.db")

vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

def generate_words_cvcvc():
    words = []
    for c1 in consonants:
        for v1 in vowels:
            for c2 in consonants:
                for v2 in vowels:
                    for c3 in consonants:
                        word = c1 + v1 + c2 + v2 + c3
                        words.append(word)
    return words

def generate_words_vcvcv():
    words = []
    for v1 in vowels:
        for c1 in consonants:
            for v2 in vowels:
                for c2 in consonants:
                    for v3 in vowels:
                        word = v1 + c1 + v2 + c2 + v3
                        words.append(word)
    return words

def generate_words_cvvcc():
    words = []
    for c1 in consonants:
        for v1 in vowels:
            for v2 in vowels:
                for c2 in consonants:
                    for c3 in consonants:
                        word = c1 + v1 + v2 + c2 + c3
                        words.append(word)
    return words


for word in generate_words_cvcvc():
    # check if word is already in the database
    if (not db.execute("SELECT * FROM domains WHERE name = ?", f"{word}.com")):
        db.execute("INSERT INTO domains (name, category) VALUES (?,?)", f"{word}.com", len(word))
        print(f"Inserted {word}.com into Database", )
    else:
        print(f"{word}.com already in Database")