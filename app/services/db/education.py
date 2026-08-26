from app.models import Education
from app.services.db.base import BaseRepository


class EducationRepository(BaseRepository[Education]):
    model = Education
    id_column = "education_id"