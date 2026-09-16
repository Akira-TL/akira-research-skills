from pathlib import Path
import unittest


HERE = Path(__file__).resolve()
REPO = next(
    parent
    for parent in HERE.parents
    if (parent / "scripts" / "check.sh").is_file()
    and (parent / "skills" / "research").is_dir()
)
SKILLS = REPO / "skills" / "research"
DOCS = REPO / "docs" / "research"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(skill: str) -> str:
    text = read(SKILLS / skill / "SKILL.md")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise AssertionError(f"{skill}/SKILL.md has no YAML frontmatter")
    return parts[1]


class ReviewSeriesContractTests(unittest.TestCase):
    def test_review_router_is_user_invoked_and_documented(self) -> None:
        self.assertTrue((SKILLS / "akira-review" / "SKILL.md").is_file())
        self.assertIn("disable-model-invocation: true", frontmatter("akira-review"))

        metadata = read(SKILLS / "akira-review" / "agents" / "openai.yaml")
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertTrue((DOCS / "akira-review.md").is_file())

    def test_review_science_is_model_invoked_and_documented(self) -> None:
        self.assertTrue((SKILLS / "review-science" / "SKILL.md").is_file())
        self.assertNotIn("disable-model-invocation", frontmatter("review-science"))

        metadata = read(SKILLS / "review-science" / "agents" / "openai.yaml")
        self.assertNotIn("allow_implicit_invocation: false", metadata)
        self.assertTrue((DOCS / "review-science.md").is_file())

    def test_repository_declares_two_primary_routers(self) -> None:
        invocation = read(REPO / ".agents" / "invocation.md")
        self.assertIn("`akira-research`", invocation)
        self.assertIn("`akira-review`", invocation)
        self.assertIn("两个顶层 user-invoked Router", invocation)

        readme = read(SKILLS / "README.md")
        self.assertIn("Research series", readme)
        self.assertIn("Review series", readme)
        self.assertIn("[`akira-review`]", readme)
        self.assertIn("[`review-science`]", readme)

    def test_research_router_no_longer_claims_the_whole_product_family(self) -> None:
        router = read(SKILLS / "akira-research" / "SKILL.md")
        self.assertIn("Research series", router)
        self.assertNotIn("科研系列 Skills 的总 Router", router)


if __name__ == "__main__":
    unittest.main()
