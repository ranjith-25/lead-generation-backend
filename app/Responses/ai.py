from pydantic import BaseModel,Field

class GetScrapedURLDataResponse(BaseModel):
    status : str = Field(...,description="Status of AI Execution.")
    job_details : dict = Field(...,description="Scraped job details of URL.")
    platform : str = Field(...,description="Platform from which data is scraped.")