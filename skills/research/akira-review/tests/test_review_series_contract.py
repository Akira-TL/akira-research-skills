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

    def test_review_literature_is_model_invoked_and_routed_before_novelty_judgment(self) -> None:
        self.assertTrue((SKILLS / "review-literature" / "SKILL.md").is_file())
        self.assertNotIn("disable-model-invocation", frontmatter("review-literature"))

        metadata = read(SKILLS / "review-literature" / "agents" / "openai.yaml")
        self.assertNotIn("allow_implicit_invocation: false", metadata)
        self.assertTrue((DOCS / "review-literature.md").is_file())

        router = read(SKILLS / "akira-review" / "SKILL.md")
        self.assertIn("review-literature", router)
        self.assertIn("closest prior work", router)

    def test_independent_review_contract_is_disclosed(self) -> None:
        router = read(SKILLS / "akira-review" / "SKILL.md")
        boundary = read(SKILLS / "akira-review" / "references" / "REVIEW-BOUNDARY.md")
        reporting = read(SKILLS / "akira-review" / "references" / "REPORTING.md")

        self.assertIn("Review Packet", router)
        self.assertIn("independent review", boundary)
        self.assertIn("project-informed mentor review", boundary)
        self.assertIn("正式同行评议", reporting)
        self.assertIn("Reviewer recommendation", reporting)

    def test_multi_pass_and_confidentiality_references_exist(self) -> None:
        multi_pass = SKILLS / "akira-review" / "references" / "MULTI-PASS.md"
        confidentiality = SKILLS / "akira-review" / "references" / "CONFIDENTIALITY.md"
        self.assertTrue(multi_pass.is_file())
        self.assertTrue(confidentiality.is_file())

        self.assertIn("isolated", read(multi_pass))
        self.assertIn("consensus", read(multi_pass).lower())
        self.assertIn("generative AI", read(confidentiality))
        self.assertIn("fail closed", read(confidentiality))

    def test_review_revision_is_model_invoked_and_routed_for_rereview(self) -> None:
        self.assertTrue((SKILLS / "review-revision" / "SKILL.md").is_file())
        self.assertNotIn("disable-model-invocation", frontmatter("review-revision"))

        metadata = read(SKILLS / "review-revision" / "agents" / "openai.yaml")
        self.assertNotIn("allow_implicit_invocation: false", metadata)
        self.assertTrue((DOCS / "review-revision.md").is_file())

        router = read(SKILLS / "akira-review" / "SKILL.md")
        rereview = read(SKILLS / "review-revision" / "SKILL.md")
        self.assertIn("review-revision", router)
        self.assertIn("evidence-before-persuasion", rereview)
        self.assertIn("response letter", rereview)
        self.assertIn("部分解决", rereview)
        self.assertIn("合理降低 Claim", rereview)

    def test_communication_routes_independent_review_without_owning_reviewer_rules(self) -> None:
        communication = read(SKILLS / "communication" / "SKILL.md")
        integrity = read(SKILLS / "communication" / "references" / "audit" / "INTEGRITY-AUDIT.md")
        revision = read(SKILLS / "communication" / "references" / "REVISION-WORKFLOW.md")

        self.assertIn("akira-review", communication)
        self.assertIn("review-revision", revision)
        self.assertNotIn("## 5. Reviewer-style 风险审查", integrity)
        self.assertNotIn("## 4. Re-review 使用 evidence-before-persuasion", revision)
        self.assertFalse(
            (SKILLS / "communication" / "references" / "audit" / "REVIEWER-STYLE-AUDIT.md").exists()
        )

    def test_review_handoff_returns_to_research_only_after_user_decision(self) -> None:
        handoff = read(SKILLS / "akira-review" / "references" / "HANDOFF.md")
        router = read(SKILLS / "akira-review" / "SKILL.md")
        research_router = read(SKILLS / "akira-research" / "SKILL.md")

        self.assertIn("用户决定", handoff)
        self.assertIn("literature", handoff)
        self.assertIn("analysis", handoff)
        self.assertIn("interpretation", handoff)
        self.assertIn("communication", handoff)
        self.assertIn("HANDOFF.md", router)
        self.assertIn("akira-review", research_router)
        current_loop_line = next(
            line for line in research_router.splitlines() if "Current Loop" in line and "可取" in line
        )
        self.assertNotIn("`REVIEW`", current_loop_line.split("它不规定下一步", 1)[0])
        self.assertIn("不增加 `REVIEW`", research_router)

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
