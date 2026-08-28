from app.models import Specialization
from app.services.db.base import BaseRepository


class SpecializationRepository(BaseRepository[Specialization]):
    model = Specialization
    id_column = "specialization_id"