"""
Hybrid matching engine for lost and found items.

Combines:
- Rule-based scoring: 60%
- TF-IDF + Cosine Similarity: 40%
"""

from typing import List, Tuple

from sqlalchemy.orm import Session

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.item import Item, ItemStatus, ItemType


class MatchingEngine:
    """Hybrid matching engine for lost and found items."""

    # Rule-based scoring
    CATEGORY_MATCH = 30
    LOCATION_MATCH = 20
    BRAND_MATCH = 20
    COLOR_MATCH = 15
    DATE_PROXIMITY = 15

    MAX_RULE_SCORE = 100

    # Date proximity threshold
    DATE_THRESHOLD = 3

    # Final score weights
    RULE_WEIGHT = 0.6
    NLP_WEIGHT = 0.4

    # Minimum score required for a possible match
    MIN_MATCH_SCORE = 0.40

    def __init__(self):
        """Initialize the TF-IDF vectorizer."""

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=100
        )

    def calculate_rule_score(
        self,
        lost_item: Item,
        found_item: Item
    ) -> float:
        """
        Calculate rule-based matching score.

        Returns:
            A normalized score between 0.0 and 1.0.
        """

        score = 0.0

        # 1. Category match
        if lost_item.category == found_item.category:
            score += self.CATEGORY_MATCH

        # 2. Location match
        if self._location_match(
            lost_item.location,
            found_item.location
        ):
            score += self.LOCATION_MATCH

        # 3. Brand match
        if lost_item.brand and found_item.brand:
            if lost_item.brand.lower() == found_item.brand.lower():
                score += self.BRAND_MATCH

        # 4. Color match
        if lost_item.color and found_item.color:
            if lost_item.color.lower() == found_item.color.lower():
                score += self.COLOR_MATCH

        # 5. Date proximity
        date_diff = abs(
            (lost_item.date_event - found_item.date_event).days
        )

        if date_diff <= self.DATE_THRESHOLD:
            score += self.DATE_PROXIMITY

        # Normalize to 0.0 - 1.0
        normalized_score = score / self.MAX_RULE_SCORE

        return min(normalized_score, 1.0)

    def calculate_nlp_score(
        self,
        lost_item: Item,
        found_item: Item
    ) -> float:
        """
        Calculate text similarity using TF-IDF
        and cosine similarity.

        Compares:
        - title
        - description

        Returns:
            A score between 0.0 and 1.0.
        """

        lost_text = (
            f"{lost_item.title} "
            f"{lost_item.description}"
        )

        found_text = (
            f"{found_item.title} "
            f"{found_item.description}"
        )

        try:
            texts = [lost_text, found_text]

            tfidf_matrix = self.vectorizer.fit_transform(texts)

            similarity = cosine_similarity(
                tfidf_matrix[0],
                tfidf_matrix[1]
            )[0][0]

            return float(similarity)

        except ValueError:
            # Happens when TF-IDF cannot create a vocabulary
            return 0.0

    def calculate_composite_score(
        self,
        rule_score: float,
        nlp_score: float
    ) -> float:
        """
        Calculate final hybrid matching score.

        Formula:
            (0.6 × rule_score) + (0.4 × nlp_score)
        """

        composite = (
            self.RULE_WEIGHT * rule_score
            + self.NLP_WEIGHT * nlp_score
        )

        return min(composite, 1.0)

    def find_matches(
        self,
        item: Item,
        db: Session,
        threshold: float | None = None
    ) -> List[Tuple[Item, float, float, float]]:
        """
        Find possible matches for an item.

        Returns:
            List of tuples:

            (
                matched_item,
                rule_score,
                nlp_score,
                total_score
            )

            sorted by total score descending.
        """

        if threshold is None:
            threshold = self.MIN_MATCH_SCORE

        # Determine opposite item type
        opposite_type = (
            ItemType.FOUND
            if item.type == ItemType.LOST
            else ItemType.LOST
        )

        # Find verified items of opposite type
        candidate_items = (
            db.query(Item)
            .filter(
                Item.type == opposite_type,
                Item.id != item.id,
                Item.status == ItemStatus.VERIFIED
            )
            .all()
        )

        matches = []

        for candidate in candidate_items:

            # Rule-based score
            rule_score = self.calculate_rule_score(
                item,
                candidate
            )

            # TF-IDF score
            nlp_score = self.calculate_nlp_score(
                item,
                candidate
            )

            # Combined score
            total_score = self.calculate_composite_score(
                rule_score,
                nlp_score
            )

            # Apply minimum threshold
            if total_score >= threshold:
                matches.append(
                    (
                        candidate,
                        rule_score,
                        nlp_score,
                        total_score
                    )
                )

        # Highest score first
        matches.sort(
            key=lambda x: x[3],
            reverse=True
        )

        return matches

    @staticmethod
    def _location_match(
        loc1: str,
        loc2: str
    ) -> bool:
        """
        Check whether two locations have
        sufficient keyword overlap.
        """

        keywords1 = set(loc1.lower().split())
        keywords2 = set(loc2.lower().split())

        if not keywords1 or not keywords2:
            return False

        overlap = keywords1.intersection(keywords2)

        # Calculate overlap relative to smaller location
        overlap_ratio = (
            len(overlap)
            / min(len(keywords1), len(keywords2))
        )

        return overlap_ratio >= 0.5

# Singleton matching engine
matcher = MatchingEngine()