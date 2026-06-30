"""Ontology Loader — loads yaml configuration files into domain models."""

from pathlib import Path

from omegaconf import OmegaConf

from hiremind.domain.ontology_models import (
    DomainNode,
    SkillNode,
    SynonymGroup,
    TechRelation,
)


class OntologyConfigLoader:
    """Loader to parse configurations for skills, synonyms, and domains."""

    def __init__(
        self,
        ontology_path: str | Path = "configs/ontology.yaml",
        synonyms_path: str | Path = "configs/synonyms.yaml",
        domains_path: str | Path = "configs/domains.yaml",
    ) -> None:
        self.ontology_path = Path(ontology_path)
        self.synonyms_path = Path(synonyms_path)
        self.domains_path = Path(domains_path)

    def load_skills(self) -> list[SkillNode]:
        """Load SkillNode definitions from ontology.yaml."""
        if not self.ontology_path.exists():
            raise FileNotFoundError(f"Ontology config not found at {self.ontology_path}")

        cfg = OmegaConf.load(self.ontology_path)
        categories = cfg.get("categories", {})
        skills: list[SkillNode] = []

        for category_name, skills_dict in categories.items():
            if not skills_dict:
                continue
            for skill_name, skill_data in skills_dict.items():
                aliases = tuple(skill_data.get("aliases", []))
                parents = tuple(skill_data.get("parents", []))
                skills.append(
                    SkillNode(
                        canonical_name=str(skill_name),
                        aliases=aliases,
                        parents=parents,
                        category=str(category_name),
                    )
                )
        return skills

    def load_protected_terms(self) -> frozenset[str]:
        """Load list of protected terms from ontology.yaml."""
        if not self.ontology_path.exists():
            return frozenset()
        cfg = OmegaConf.load(self.ontology_path)
        protected = cfg.get("protected_terms", [])
        return frozenset(str(term) for term in protected)

    def load_relationships(self) -> list[TechRelation]:
        """Load TechRelation definitions from ontology.yaml."""
        if not self.ontology_path.exists():
            return []

        cfg = OmegaConf.load(self.ontology_path)
        relationships_dict = cfg.get("technology_relationships", {})
        relations: list[TechRelation] = []

        if not relationships_dict:
            return []

        for source, rels in relationships_dict.items():
            if not rels:
                continue
            for rel_type, targets in rels.items():
                if not targets:
                    continue
                # Normalize relation type to uppercase (e.g. uses -> USES)
                type_upper = rel_type.upper()
                for target in targets:
                    relations.append(
                        TechRelation(
                            source=str(source),
                            target=str(target),
                            relation_type=type_upper,
                        )
                    )
        return relations

    def load_synonyms(self) -> list[SynonymGroup]:
        """Load SynonymGroup definitions from synonyms.yaml."""
        if not self.synonyms_path.exists():
            return []

        cfg = OmegaConf.load(self.synonyms_path)
        groups = cfg.get("synonym_groups", [])
        synonym_list: list[SynonymGroup] = []

        for group in groups:
            if not group or len(group) == 0:
                continue
            canonical = str(group[0])
            terms = tuple(str(t) for t in group)
            synonym_list.append(SynonymGroup(canonical=canonical, terms=terms))

        return synonym_list

    def load_domains(self) -> list[DomainNode]:
        """Load DomainNode definitions from domains.yaml."""
        if not self.domains_path.exists():
            return []

        cfg = OmegaConf.load(self.domains_path)
        domains_dict = cfg.get("domains", {})
        domain_list: list[DomainNode] = []

        for domain_name, data in domains_dict.items():
            label = data.get("label", "")
            skills = tuple(str(s) for s in data.get("skills", []))
            subdomains = tuple(str(sd) for sd in data.get("subdomains", []))
            domain_list.append(
                DomainNode(
                    name=str(domain_name),
                    label=str(label),
                    skills=skills,
                    subdomains=subdomains,
                )
            )

        return domain_list
