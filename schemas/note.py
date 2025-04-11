def note_entity(item) -> dict:
    """Returns data recieved from database as a dictionary"""
    return {
        "_id": str([item["_id"]]),
        "title": item["title"],
        "description": item["description"],
        "important": item["important"],
    }


def notes_entity(items) -> list:
    """Sends recieved data from database to be converted into a dictionary"""
    return [note_entity(item) for item in items]
