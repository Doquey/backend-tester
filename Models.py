from pydantic import BaseModel


class JobStarter(BaseModel):
    stocks: list
    method: int
    years: int
    initial_investiment: float
