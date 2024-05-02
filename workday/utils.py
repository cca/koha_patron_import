# abstraction over JSON files that are either straight lists (made by our scripts)
# or Workday JSON files with a "Report_Entry" key
def get_entries(data) -> list[dict]:
    if type(data) == list:
        return data
    elif data.get("Report_Entry"):
        return data["Report_Entry"]
    else:
        raise Exception(
            "Could not find list of users in JSON data—are you sure this is the right file?"
        )
