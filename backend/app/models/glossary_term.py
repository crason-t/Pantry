import enum

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class GlossaryCategory(str, enum.Enum):
    FLAVOR = "flavor"
    TECHNIQUE = "technique"
    REACTION = "reaction"


class GlossaryTerm(Base):
    """Shared reference data: fixed, curated definitions, not tied to any one
    recipe. Seeded once (migration/fixture), not regenerated per ingestion."""

    __tablename__ = "glossary_terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[GlossaryCategory] = mapped_column(Enum(GlossaryCategory, name="glossary_category"))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    definition: Mapped[str] = mapped_column(Text)

    insights: Mapped[list["RecipeInsight"]] = relationship(back_populates="glossary_term")
