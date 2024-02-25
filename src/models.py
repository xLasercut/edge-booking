from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.constants import ISO_TIME_FORMAT, QUERY_TIME_FORMAT


class BookingCardDetails(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    activity: str
    location: str
    start_time: str
    spaces_left: str


class UserCredentials(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    jwt: str
    pid: str


class ActivityDetails(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

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
    model_config = ConfigDict(str_strip_whitespace=True)

    SubLocationGroupId: int
    SubLocationNames: str
    Available: bool
