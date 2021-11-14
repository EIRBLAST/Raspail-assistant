from datetime import date, datetime, timedelta
import json

DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]
COLLOSCOPE = json.load(open("datas/colloscope.json", "r"))
EDT = json.load(open("datas/edt.json", "r"))


def get_week_parity(day: datetime.date) -> int:
    """Return the parity of the week containing the day.

    Args:
        day (datetime.date): A day of the week.

    Returns:
        [int]: 0 if the week is `paire` 1 if it's `impaire`.
    """
    monday = day - timedelta(days=day.weekday())
    column_index = COLLOSCOPE["mondays"].index(monday.strftime("%d/%m/%Y"))

    return COLLOSCOPE["weeknumber"][column_index] % 2


def informatique_parity(day: datetime.date) -> str:
    """Return rotation of informatique of the given day/week.

    Args:
        day (datetime.date): The day

    Returns:
        str: 'prair' /  'imaire' / 'entier'
    """
    monday = day - timedelta(days=day.weekday())
    column_index = COLLOSCOPE["mondays"].index(monday.strftime("%d/%m/%Y"))
    res = COLLOSCOPE["informatique"][column_index]
    return 'pair'*(res == 'B') + 'impair'*(res == 'A') + 'entier'*(res == 'C')


def IsParite(parite: str, group_number: int, week_parite: int) -> bool:
    """This function compute if the group attend the course.

    Args:
        parite (str): The parite string.
        group_number (int): The group id.
        week_parite (int): The week parity.

    Returns:
        bool: Wether the group attend or not.
    """
    if parite == 'entier':
        return True
    if parite == 'pair':
        return group_number % 2 != week_parite
    elif parite == 'impair':
        return group_number % 2 == week_parite
    else:
        return True

def get_events_of_the_day(day: datetime.date, grp: int) -> list:
    """Return a list of events of the day `day` of group `grp`

    Args:
        day (datetime.date): The day.
        grp (int): The group.

    Returns:
        [list]: A list of events including `colles`, `tp` and `cours`.
    """

    day_index = day.weekday()
    
    monday = day - timedelta(days=day_index)
    column_index = COLLOSCOPE["mondays"].index(monday.strftime(f"%d/%m/%Y"))

    # Colles & TP

    events = []
    for line in COLLOSCOPE["planning"]:
        if line["grps"][column_index] == int(grp) and line["timedelta"]["days"] == day_index:
            events.append(line)

    # Cours

    for c in EDT[day_index]["cours"]:

        if IsParite(c["parite"], grp, get_week_parity(day)):
            events.append(c)

    events.sort(key=lambda line: timedelta(**line["timedelta"]))
    return events


