from types import SimpleNamespace
from typing import Literal

from .config import config
from .request_wrapper import request_wrapper

PATRON_READ_ONLY_FIELDS: tuple[
    Literal["anonymized"],
    Literal["expired"],
    Literal["restricted"],
    Literal["updated_on"],
] = ("anonymized", "expired", "restricted", "updated_on")


class Patron(SimpleNamespace):
    def __init__(self, patron_id):
        self.patron_id = patron_id
        if patron_id is None:
            raise Exception(
                "Cannot instantiate Patron object without a Patron ID parameter."
            )
        self.get()

    def __repr__(self):
        return "{} {} ({})".format(self.firstname, self.surname, self.patron_id)

    def remove_readonly_fields(self):
        # utility method, we must do this before attempting write API operations
        patron = self.__dict__.copy()
        for field in PATRON_READ_ONLY_FIELDS:
            patron.pop(field, None)
        return patron

    def delete(self):
        http = request_wrapper()
        if http is None:
            raise Exception("Failed to create HTTP session")
        response = http.delete(
            "{}/patrons/{}".format(config["api_root"], self.patron_id)
        )
        response.raise_for_status()
        return self

    def get(self):
        # sync local object with Koha data from API, used in __init__
        http = request_wrapper()
        if http is None:
            raise Exception("Failed to create HTTP session")
        response = http.get(
            "{}/patrons/{}".format(
                config["api_root"],
                self.patron_id,
            )
        )
        response.raise_for_status()
        for key, value in response.json().items():
            setattr(self, key, value)
        return self

    def get_attributes(self):
        # get all extended attributes
        http = request_wrapper()
        if http is None:
            raise Exception("Failed to create HTTP session")
        response = http.get(
            "{}/patrons/{}/extended_attributes".format(
                config["api_root"], self.patron_id
            )
        )
        response.raise_for_status()
        self.extended_attributes = response.json()
        return self

    def update(self):
        # sync local object to Koha
        http = request_wrapper()
        if http is None:
            raise Exception("Failed to create HTTP session")
        response = http.put(
            "{}/patrons/{}".format(
                config["api_root"],
                self.patron_id,
            ),
            json=self.remove_readonly_fields(),
        )
        response.raise_for_status()
        return self
