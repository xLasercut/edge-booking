from dataclasses import dataclass


@dataclass
class BookingCardDetails:
    activity: str
    location: str
    start_time: str
    spaces_left: str
