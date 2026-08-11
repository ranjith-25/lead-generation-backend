from pydantic import BaseModel,Field
from uuid import UUID

class GetScrapedURLDataResponse(BaseModel):
    status : str = Field(...,description="Status of AI Execution.")
    job_details : dict = Field(...,description="Scraped job details of URL.")
    platform : str = Field(...,description="Platform from which data is scraped.")
    company_profile: dict | None = Field(None, description="Company profile data")

class AIProjectResponse(BaseModel):
    project_id : UUID = Field(...,description="ProjectID")
    project_name : str = Field(...,description="Matched Project Name")
    match_score : float = Field(...,description="Matched score 0-1")
    justification : str = Field(...,description="Reason why this project is selected")
    matched_evidence : list[str] = Field(default_factory=list,description="Evidence from AI")

class GetRelaventProjectResponse(BaseModel):
    status : str = Field(...,description="Status of AI Execution.")
    matches : list[AIProjectResponse] = Field(default_factory=list,description="Matched Projects.")

class AISalesEnablementResponse(BaseModel):
    status : str = Field(...,description="Status of AI Execution.")
    discovery_questions : list[str] = Field(
        default_factory=list,
        description="Questions to gather additional information about the opportunity."
    )
    talking_points : list[str] = Field(
        default_factory=list,
        description="Key talking points for sales outreach."
    )
    outreach_template : str = Field(
        ...,
        description="Generated outreach message template."
    )


class AIMatchedProfiles(BaseModel):
    candidate_id : UUID = Field(...,description="CandidateID")
    candidate_name : str = Field(...,description="Candidate Name")
    email : str = Field(...,description="Candidate Email")
    variant_id : UUID = Field(...,description="VariantID")
    variant_title : str = Field(...,description="Variant Title")
    experience_years : float = Field(...,description="Experience Years")
    match_percentage : float = Field(...,description="Match Percentage")
    matching_skills : list[str] = Field(default_factory=list,description="Matching Skills")
    missing_skills : list[str] = Field(default_factory=list,description="Missing Skills")
    justification : str = Field(...,description="Reason why this profile is selected")


class GetMatchedProfilesResponse(BaseModel):
    status : str = Field(...,description="Status of AI Execution.")
    matches : list[AIMatchedProfiles] = Field(default_factory=list,description="Matched Profiles.")
    error_message : str | None = Field(None,description="Error message")
