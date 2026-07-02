"""Generate 5000+ realistic dummy courses into MongoDB (DDD Section 10.1).

Strategy:
  - 12 categories x ~45 skills = ~540 unique skills
  - Each skill -> 8-12 courses across 4 levels -> ~5000-6000 courses
  - Level distribution ~30% Beginner / 30% Intermediate / 25% Advanced / 15% Expert
  - course_id: COURSE-{CATEGORY_CODE}-{LEVEL_CODE}-{SEQ}
  - All courses inserted with is_embedded=false

Run:  python scripts/generate_courses.py [--reset]

Uses pymongo (sync) directly so it can run standalone, independent of the
FastAPI app. Reads connection settings from backend/.env via app.config.
"""
from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import datetime, timezone

# Allow running as `python scripts/generate_courses.py` from backend/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# NOTE: MongoClient / get_settings are imported lazily inside main() so that
# build_courses() can be unit-tested without the DB stack installed.
from app.constants.categories import CATEGORY_CODES, SkillCategory  # noqa: E402

random.seed(42)

LEVELS = [
    ("Beginner", 1, "BEG"),
    ("Intermediate", 2, "INT"),
    ("Advanced", 3, "ADV"),
    ("Expert", 4, "EXP"),
]
LEVEL_WEIGHTS = [0.30, 0.30, 0.25, 0.15]

PROVIDERS = [
    "Coursera", "Udemy", "Pluralsight", "edX", "O'Reilly",
    "LinkedIn Learning", "Educative", "Codecademy", "DataCamp",
    "Microsoft Learn", "Google Cloud Training", "AWS Training",
]

TITLE_TEMPLATES = {
    "Beginner": [
        "{skill} Fundamentals",
        "Introduction to {skill}",
        "Getting Started with {skill}",
        "{skill} for Beginners",
        "{skill} Essentials",
    ],
    "Intermediate": [
        "{skill} in Practice",
        "Building with {skill}",
        "Practical {skill}",
        "Applied {skill}",
        "Hands-On {skill}",
    ],
    "Advanced": [
        "Advanced {skill}",
        "{skill} Deep Dive",
        "Mastering {skill}",
        "Professional {skill}",
        "{skill} Advanced Techniques",
    ],
    "Expert": [
        "{skill} Architecture",
        "{skill} at Scale",
        "Expert {skill}",
        "{skill} in Production",
        "{skill} for Architects",
    ],
}

DESC_TEMPLATES = {
    "Beginner": (
        "A beginner-friendly course covering the core concepts of {skill}. "
        "Learn the fundamentals through guided examples and hands-on exercises, "
        "building a solid foundation for further study."
    ),
    "Intermediate": (
        "Take your {skill} skills to the next level. This intermediate course "
        "focuses on real-world application, practical patterns, and building "
        "projects that reinforce working knowledge of {skill}."
    ),
    "Advanced": (
        "Master advanced {skill} concepts including complex patterns, performance "
        "optimization, and best practices for production systems. Designed for "
        "practitioners with solid prior experience in {skill}."
    ),
    "Expert": (
        "An expert-level deep dive into {skill} architecture, scalability, and "
        "leadership. Explore design trade-offs, large-scale system concerns, and "
        "the strategic use of {skill} across an organization."
    ),
}

DURATION_RANGES = {
    "Beginner": (10, 25),
    "Intermediate": (20, 40),
    "Advanced": (25, 50),
    "Expert": (30, 60),
}

PREREQ_BY_LEVEL = {
    "Beginner": [],
    "Intermediate": ["Introduction to {skill}", "Basic Programming"],
    "Advanced": ["Intermediate {skill}", "OOP Concepts", "Data Structures"],
    "Expert": ["Advanced {skill}", "System Design", "Distributed Systems"],
}

# ---------------------------------------------------------------------------
# Skill taxonomy: ~45 skills per category (12 categories -> ~540 skills).
# ---------------------------------------------------------------------------
SKILLS_BY_CATEGORY = {
    SkillCategory.PROGRAMMING_LANGUAGES: [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
        "Ruby", "PHP", "Kotlin", "Swift", "Scala", "Elixir", "Haskell", "Perl",
        "R", "Julia", "Dart", "Clojure", "Erlang", "F#", "Groovy", "Lua",
        "Objective-C", "Assembly", "COBOL", "Fortran", "Bash Scripting", "PowerShell",
        "SQL Programming", "MATLAB", "Visual Basic", "Solidity", "WebAssembly",
        "Zig", "Nim", "Crystal", "OCaml", "Racket", "Scheme", "Prolog", "Ada",
        "Delphi", "VHDL",
    ],
    SkillCategory.FRONTEND: [
        "React", "Angular", "Vue.js", "Svelte", "Next.js", "Nuxt.js", "CSS",
        "Tailwind CSS", "Sass", "HTML5", "JavaScript DOM", "TypeScript Frontend",
        "Redux", "MobX", "Webpack", "Vite", "Babel", "Styled Components",
        "Material UI", "Bootstrap", "Responsive Design", "Web Accessibility",
        "Progressive Web Apps", "Web Components", "GraphQL Client", "Apollo Client",
        "Jest", "React Testing Library", "Cypress", "Storybook", "Figma to Code",
        "Animation with CSS", "Three.js", "D3.js", "Chart.js", "SEO Fundamentals",
        "Micro Frontends", "Server-Side Rendering", "Ember.js", "Solid.js",
        "Alpine.js", "Web Performance", "Browser DevTools", "PWA Offline", "Gatsby",
    ],
    SkillCategory.BACKEND: [
        "FastAPI", "Django", "Flask", "Spring Boot", "Node.js", "Express.js",
        "NestJS", "REST API Design", "GraphQL Server", "gRPC", "Ruby on Rails",
        "Laravel", "ASP.NET Core", "Gin", "Fiber", "Ktor", "Micronaut", "Quarkus",
        "WebSockets", "Message Queues", "RabbitMQ", "API Gateway", "Authentication",
        "OAuth2", "JWT", "Session Management", "Rate Limiting", "Caching Strategies",
        "Background Jobs", "Celery", "Webhooks", "OpenAPI", "Serverless Functions",
        "API Versioning", "Middleware Design", "ORM Patterns", "SQLAlchemy",
        "Hibernate", "Prisma", "Pagination", "File Uploads", "Email Services",
        "Payment Integration", "Backend Security", "Dependency Injection",
    ],
    SkillCategory.DATABASES: [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
        "DynamoDB", "SQLite", "MariaDB", "Oracle DB", "SQL Server", "Neo4j",
        "CouchDB", "InfluxDB", "TimescaleDB", "CockroachDB", "Firestore",
        "Database Indexing", "Query Optimization", "Database Sharding",
        "Replication", "ACID Transactions", "Database Normalization", "NoSQL Design",
        "Data Modeling", "Stored Procedures", "Database Migration", "Connection Pooling",
        "Full-Text Search", "Vector Databases", "Pinecone", "ChromaDB", "Weaviate",
        "Database Backup", "Partitioning", "Materialized Views", "CTEs",
        "Window Functions", "Database Security", "Redis Streams", "Graph Queries",
        "Time Series Data", "Change Data Capture", "Database Monitoring", "PL/SQL",
    ],
    SkillCategory.DEVOPS: [
        "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible", "GitLab CI",
        "GitHub Actions", "CircleCI", "ArgoCD", "Helm", "Prometheus", "Grafana",
        "CI/CD Pipelines", "Infrastructure as Code", "Container Orchestration",
        "Service Mesh", "Istio", "Linkerd", "Vault", "Consul", "Packer",
        "Nginx", "HAProxy", "Load Balancing", "Log Aggregation", "ELK Stack",
        "Datadog", "New Relic", "PagerDuty", "Site Reliability Engineering",
        "GitOps", "Blue-Green Deployment", "Canary Deployment", "Configuration Management",
        "Bash Automation", "Monitoring & Alerting", "Chaos Engineering", "Podman",
        "Docker Compose", "Kustomize", "Secrets Management", "Observability",
        "Incident Response", "Infrastructure Monitoring", "FluxCD",
    ],
    SkillCategory.CLOUD: [
        "AWS", "GCP", "Azure", "AWS Lambda", "AWS EC2", "AWS S3", "AWS RDS",
        "AWS ECS", "AWS EKS", "AWS CloudFormation", "AWS IAM", "AWS VPC",
        "Azure Functions", "Azure DevOps", "Azure Kubernetes Service", "GCP Compute Engine",
        "Google Kubernetes Engine", "Cloud Run", "BigQuery", "Cloud Storage",
        "Serverless Architecture", "Cloud Cost Optimization", "Cloud Security",
        "Multi-Cloud Strategy", "CloudFront", "Route 53", "API Gateway Cloud",
        "Cloud Networking", "Cloud Migration", "CloudWatch", "Terraform Cloud",
        "Cloud Load Balancing", "Auto Scaling", "Cloud Identity", "Pub/Sub",
        "Cloud Functions", "Cloud SQL", "Firebase", "CDN Configuration",
        "Cloud Monitoring", "Disaster Recovery", "Edge Computing", "Cloud Backup",
        "Cloud Architecture", "Well-Architected Framework",
    ],
    SkillCategory.ARCHITECTURE: [
        "System Design", "Microservices", "Event-Driven Architecture",
        "Domain-Driven Design", "Monolith to Microservices", "API Design",
        "Distributed Systems", "CQRS", "Event Sourcing", "Saga Pattern",
        "Hexagonal Architecture", "Clean Architecture", "Layered Architecture",
        "Service-Oriented Architecture", "Serverless Design", "Scalability Patterns",
        "High Availability", "Fault Tolerance", "Caching Architecture",
        "Load Balancing Design", "Database Architecture", "Message-Driven Design",
        "API Gateway Pattern", "Circuit Breaker", "Bulkhead Pattern", "Strangler Fig",
        "Design Patterns", "SOLID Principles", "Architecture Decision Records",
        "C4 Model", "Enterprise Architecture", "Data Mesh", "Micro Frontends Architecture",
        "Backend for Frontend", "Idempotency Design", "Consistency Models",
        "CAP Theorem", "Sharding Strategy", "Rate Limiting Design",
        "Observability Design", "Multi-Tenancy", "Modular Monolith",
        "Reactive Architecture", "Zero Trust Architecture", "Capacity Planning",
    ],
    SkillCategory.DATA_ENGINEERING: [
        "Apache Spark", "Apache Airflow", "ETL Pipelines", "Apache Kafka", "dbt",
        "Data Warehousing", "Data Lakes", "Snowflake", "Databricks", "Apache Flink",
        "Apache Beam", "Hadoop", "Hive", "Presto", "Delta Lake", "Data Modeling",
        "Stream Processing", "Batch Processing", "Data Pipeline Orchestration",
        "ELT", "Data Quality", "Data Governance", "Apache NiFi", "Luigi",
        "Prefect", "Dagster", "Fivetran", "Airbyte", "Change Data Capture",
        "Data Ingestion", "Parquet", "Avro", "Data Partitioning", "Data Catalog",
        "Master Data Management", "Data Vault", "Star Schema", "Kimball Modeling",
        "Real-Time Analytics", "Data Observability", "Great Expectations",
        "Kafka Streams", "Schema Registry", "Data Lineage", "Lakehouse",
    ],
    SkillCategory.DATA_SCIENCE: [
        "Machine Learning", "Deep Learning", "Natural Language Processing",
        "Statistics", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
        "Data Visualization", "Feature Engineering", "Model Deployment", "MLOps",
        "Computer Vision", "Reinforcement Learning", "Time Series Analysis",
        "Regression Analysis", "Classification", "Clustering", "Neural Networks",
        "Transformers", "LLMs", "Prompt Engineering", "RAG Systems", "Embeddings",
        "Hugging Face", "Keras", "XGBoost", "Random Forests", "Gradient Boosting",
        "Hyperparameter Tuning", "Model Evaluation", "A/B Testing", "Bayesian Statistics",
        "Recommender Systems", "Anomaly Detection", "Data Cleaning", "Jupyter Notebooks",
        "Matplotlib", "Seaborn", "MLflow", "Model Monitoring", "Vector Search",
        "Fine-Tuning", "Generative AI",
    ],
    SkillCategory.QUALITY: [
        "Unit Testing", "Integration Testing", "Test-Driven Development", "Selenium",
        "Pytest", "JUnit", "End-to-End Testing", "Cypress Testing", "Playwright",
        "Test Automation", "Behavior-Driven Development", "Mocking", "Code Coverage",
        "Performance Testing", "Load Testing", "JMeter", "Contract Testing",
        "API Testing", "Postman", "Regression Testing", "Smoke Testing",
        "Acceptance Testing", "Property-Based Testing", "Mutation Testing",
        "Test Fixtures", "Continuous Testing", "Testing Pyramid", "Snapshot Testing",
        "Visual Regression Testing", "Accessibility Testing", "Security Testing",
        "Fuzz Testing", "Chaos Testing", "Test Data Management", "Cucumber",
        "TestNG", "Mockito", "Jest Testing", "Vitest", "Robot Framework",
        "Karate", "Gatling", "k6", "QA Strategy", "Test Case Design",
    ],
    SkillCategory.SECURITY: [
        "OWASP Top 10", "Authentication Security", "Encryption", "Penetration Testing",
        "Web Application Security", "Network Security", "Cryptography", "TLS/SSL",
        "OAuth Security", "SAML", "Zero Trust", "Threat Modeling", "SQL Injection Defense",
        "XSS Prevention", "CSRF Protection", "Security Auditing", "Vulnerability Scanning",
        "SIEM", "Incident Response", "Secure Coding", "Identity and Access Management",
        "Secrets Management", "Container Security", "Cloud Security Posture",
        "API Security", "DevSecOps", "Static Analysis", "Dynamic Analysis",
        "Fuzzing", "Reverse Engineering", "Malware Analysis", "Firewall Configuration",
        "IDS/IPS", "Security Compliance", "GDPR Compliance", "SOC 2", "PCI DSS",
        "Key Management", "PKI", "Multi-Factor Authentication", "Password Security",
        "Security Monitoring", "Digital Forensics", "Red Teaming", "Blue Teaming",
    ],
    SkillCategory.SOFT_SKILLS: [
        "Communication", "Mentoring", "Project Management", "Agile", "Scrum",
        "Kanban", "Leadership", "Team Collaboration", "Conflict Resolution",
        "Time Management", "Public Speaking", "Technical Writing", "Presentation Skills",
        "Stakeholder Management", "Negotiation", "Emotional Intelligence",
        "Critical Thinking", "Problem Solving", "Decision Making", "Active Listening",
        "Coaching", "Delegation", "Feedback Delivery", "Cross-Functional Collaboration",
        "Change Management", "Strategic Thinking", "Adaptability", "Creativity",
        "Facilitation", "Product Thinking", "Customer Empathy", "Prioritization",
        "Remote Collaboration", "Cultural Awareness", "Networking", "Interviewing",
        "Onboarding", "Retrospective Facilitation", "OKR Planning", "Roadmapping",
        "Risk Management", "Budgeting", "Vendor Management", "Estimation",
        "Documentation",
    ],
}


def _weighted_rating() -> float:
    """Ratings 3.5-5.0, weighted toward 4.0-4.8."""
    base = random.choices(
        population=[
            random.uniform(3.5, 4.0),
            random.uniform(4.0, 4.8),
            random.uniform(4.8, 5.0),
        ],
        weights=[0.2, 0.65, 0.15],
    )[0]
    return round(base, 1)


def _secondary_tags(skill: str, pool: list[str]) -> list[str]:
    """1-3 related secondary skill tags from the same category."""
    others = [s for s in pool if s != skill]
    k = min(len(others), random.randint(1, 3))
    return random.sample(others, k) if k > 0 else []


def _prerequisites(skill: str, level_label: str) -> list[str]:
    templates = PREREQ_BY_LEVEL[level_label]
    return [t.format(skill=skill) for t in templates][:3]


def build_courses() -> list[dict]:
    courses: list[dict] = []
    seq_counters: dict[tuple[str, str], int] = {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for category, skills in SKILLS_BY_CATEGORY.items():
        cat_code = CATEGORY_CODES[category]
        for skill in skills:
            num_courses = random.randint(8, 12)
            level_labels = [lbl for (lbl, _n, _c) in LEVELS]
            chosen_levels = random.choices(
                level_labels, weights=LEVEL_WEIGHTS, k=num_courses
            )
            for level_label in chosen_levels:
                level_numeric = next(n for (lbl, n, _c) in LEVELS if lbl == level_label)
                level_code = next(c for (lbl, _n, c) in LEVELS if lbl == level_label)

                key = (cat_code, level_code)
                seq_counters[key] = seq_counters.get(key, 0) + 1
                seq = seq_counters[key]
                course_id = f"COURSE-{cat_code}-{level_code}-{seq:03d}"

                title = random.choice(TITLE_TEMPLATES[level_label]).format(skill=skill)
                provider = random.choice(PROVIDERS)
                low, high = DURATION_RANGES[level_label]
                duration = random.randint(low, high)
                slug = title.lower().replace(" ", "-").replace(":", "").replace("'", "")

                courses.append(
                    {
                        "course_id": course_id,
                        "title": title,
                        "provider": provider,
                        "platform_url": f"https://{provider.split()[0].lower()}.com/learn/{slug}",
                        "skill_tags": [skill] + _secondary_tags(skill, skills),
                        "primary_category": category.value,
                        "level": level_label,
                        "level_numeric": level_numeric,
                        "duration_hours": duration,
                        "description": DESC_TEMPLATES[level_label].format(skill=skill),
                        "prerequisites": _prerequisites(skill, level_label),
                        "rating": _weighted_rating(),
                        "is_embedded": False,
                        "created_at": now,
                    }
                )
    return courses


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate dummy courses into MongoDB")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete all existing courses before inserting (default behavior regenerates cleanly).",
    )
    args = parser.parse_args()

    from pymongo import MongoClient

    from app.config import get_settings

    settings = get_settings()
    if settings.mongodb_uri.startswith("your-mongodb"):
        print("ERROR: MONGODB_URI is not configured in backend/.env")
        sys.exit(1)

    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=10000)
    db = client[settings.mongodb_db_name]
    collection = db["course_catalog"]

    # Ensure unique index on course_id.
    collection.create_index("course_id", unique=True)

    print("Generating courses...")
    courses = build_courses()
    print(f"Generated {len(courses)} courses across {len(SKILLS_BY_CATEGORY)} categories.")

    # Regenerate cleanly to keep is_embedded flags consistent.
    print("Clearing existing course_catalog...")
    collection.delete_many({})

    print("Inserting into MongoDB (this may take a moment)...")
    BATCH = 1000
    inserted = 0
    for i in range(0, len(courses), BATCH):
        chunk = courses[i : i + BATCH]
        collection.insert_many(chunk, ordered=False)
        inserted += len(chunk)
        print(f"  inserted {inserted}/{len(courses)}")

    total = collection.count_documents({})
    unembedded = collection.count_documents({"is_embedded": False})
    print(f"Done. course_catalog now has {total} courses ({unembedded} unembedded).")
    client.close()


if __name__ == "__main__":
    main()
