from datetime import datetime

from pydantic import BaseModel

from src.constants import ISO_TIME_FORMAT, QUERY_TIME_FORMAT


class BookingCardDetails(BaseModel):
    activity: str
    location: str
    start_time: str
    spaces_left: str


class UserCredentials(BaseModel):
    jwt: str
    pid: str


class ActivityDetails(BaseModel):
    ActivityCode: str
    LocationCode: str
    LocationDescription: str
    ActivityGroupId: str
    ActivityDescription: str
    StartTime: str
    EndTime: str
    AvailablePlaceLocationDescription: str
    DisplayName: str

    def query_start_time(self) -> str:
        return datetime.strptime(self.StartTime, ISO_TIME_FORMAT).strftime(
            QUERY_TIME_FORMAT
        )

    def query_end_time(self) -> str:
        return datetime.strptime(self.EndTime, ISO_TIME_FORMAT).strftime(
            QUERY_TIME_FORMAT
        )


class ActivitySubLocationDetails(BaseModel):
    SubLocationGroupId: int
    SubLocationNames: str
    Available: bool
