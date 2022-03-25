# Score the the day from 0 to 10

def score(day: list]) -> int:
    """Score the day from 0 to 10.

    Args:
        day (list[list]): The day to score.

    Returns:
        int: The score of the day.
    """
    score = 0
    
    
    # We can have a maximum of 9 hours of courses per day
    # So we have a score of 0 if we have 9 hours of courses and 1 if we have 0 hours

    day_weight =  1 - sum([c["duration"]["hours"] for c in day ])/9

    # If we have holes in the day, we have a lower score exept if it beetween 12:00 and 14:00 or 11:00 and 13:00

    hours = [0]*9
    for c in day:
        p = c["timedelta"]["hours"] - 8
        for l in range(c["duration"]["hours"]):
            hours[p+l] = 1
    
    print(hours)

    # Exemple of a day
    # [0,1,1,1,0,0,0,1,0]

    # Find holes

    holes  = []
    c = 0

    # while c < len(holes) - 1:
    #     if c - 1 > 0 and hours[c-1] == 1 and hours[c] == 0 and  c + 1 < len(hours) -1 and 1 in hours[c+1:]:
    #         holes.append(1)
    #     c += 1

    # find the range of holes
    i = 0
    print(len(hours))
    while i <= len(hours) - 1 :
        if hours[i] == 0:
            a = i
            b = i 
            while i <= len(hours) - 1  and  hours[i] == 0 :
                print(i)
                b += 1
                i += 1 # if i < len(hours) - 1 else 0
            holes.append([a,b])
        else:
            i += 1

    holes = [(i[0] + 8,i[1] + 8) for i in holes]

    return day_weight, hours,  holes
