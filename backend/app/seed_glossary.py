"""Seed fixture for GlossaryTerm reference data.

GlossaryTerm content is fixed domain knowledge (a finite, well-known set of
flavor elements, techniques, and food-science reactions), not generated per
recipe -- see docs/MVP.md. Run with: `uv run python -m app.seed_glossary`.
Idempotent: skips any slug that already exists.
"""

from app.db import SessionLocal
from app.models.glossary_term import GlossaryCategory, GlossaryTerm

GLOSSARY_FIXTURE: list[dict] = [
    {
        "category": GlossaryCategory.TECHNIQUE,
        "slug": "sear",
        "name": "Searing",
        "definition": "Cooking the surface of food at high heat, usually in fat, until browned.",
    },
    {
        "category": GlossaryCategory.TECHNIQUE,
        "slug": "braise",
        "name": "Braising",
        "definition": "Searing food, then cooking it slowly in a small amount of liquid at low heat.",
    },
    {
        "category": GlossaryCategory.TECHNIQUE,
        "slug": "deglaze",
        "name": "Deglazing",
        "definition": "Adding liquid to a hot pan to lift browned bits (fond) stuck to the bottom.",
    },
    {
        "category": GlossaryCategory.REACTION,
        "slug": "maillard_reaction",
        "name": "Maillard reaction",
        "definition": (
            "A chemical reaction between amino acids and reducing sugars, triggered by heat, "
            "that produces browning and hundreds of new flavor/aroma compounds."
        ),
    },
    {
        "category": GlossaryCategory.REACTION,
        "slug": "caramelization",
        "name": "Caramelization",
        "definition": "The browning of sugar itself under heat, distinct from the Maillard reaction.",
    },
    {
        "category": GlossaryCategory.REACTION,
        "slug": "emulsification",
        "name": "Emulsification",
        "definition": "Dispersing two normally-immiscible liquids (like oil and water) into a stable mixture.",
    },
    {
        "category": GlossaryCategory.FLAVOR,
        "slug": "acidity",
        "name": "Acidity",
        "definition": "Sourness that brightens a dish and balances rich, fatty, or sweet flavors.",
    },
    {
        "category": GlossaryCategory.FLAVOR,
        "slug": "umami",
        "name": "Umami",
        "definition": "A savory taste from glutamates and nucleotides, often described as meaty or brothy.",
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        existing_slugs = {row[0] for row in db.query(GlossaryTerm.slug).all()}
        added = 0
        for entry in GLOSSARY_FIXTURE:
            if entry["slug"] in existing_slugs:
                continue
            db.add(GlossaryTerm(**entry))
            added += 1
        db.commit()
        print(f"Seeded {added} glossary term(s); {len(GLOSSARY_FIXTURE) - added} already present.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
