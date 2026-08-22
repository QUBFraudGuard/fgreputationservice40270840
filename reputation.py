import time
import hashlib

def reputation_check(card, KNOWN_BAD_CARDS):

     # simulate some processing delay, like a real external lookup would have
    time.sleep(0.2)
  
    if card in KNOWN_BAD_CARDS:
        score = KNOWN_BAD_CARDS[card]
    else:
       
        score = int(hashlib.md5(card.encode()).hexdigest(), 16) % 100

    result = {"card": card, "risk_score": score}

    return result