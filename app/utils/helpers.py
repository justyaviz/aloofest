import random


def generate_fest_id():

    num = random.randint(1,999)

    return f"FEST-{num:03d}"
