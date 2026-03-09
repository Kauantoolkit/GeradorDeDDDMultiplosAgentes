"""Mappers for membership."""
from application.dtos import MemberDTO
from domain.membership_entities import Member

class MemberMapper:
    @staticmethod
    def to_dto(entity: Member) -> MemberDTO:
        return MemberDTO(id=entity.id)
