// Shared 12-category taxonomy (mirrors backend/app/constants/categories.py).
// Single source of truth for the frontend.

export const CATEGORIES = [
  { key: "programming_languages", label: "Programming Languages" },
  { key: "frontend", label: "Frontend Development" },
  { key: "backend", label: "Backend Development" },
  { key: "databases", label: "Databases" },
  { key: "devops", label: "DevOps & Infrastructure" },
  { key: "cloud", label: "Cloud Platforms" },
  { key: "architecture", label: "System Architecture" },
  { key: "data_engineering", label: "Data Engineering" },
  { key: "data_science", label: "Data Science & ML" },
  { key: "quality", label: "Quality & Testing" },
  { key: "security", label: "Security" },
  { key: "soft_skills", label: "Soft Skills & Leadership" },
];

export const CATEGORY_LABELS = CATEGORIES.reduce((acc, c) => {
  acc[c.key] = c.label;
  return acc;
}, {});

export function categoryLabel(key) {
  return CATEGORY_LABELS[key] || key;
}

export const PROFICIENCY_LABELS = {
  1: "Beginner",
  2: "Intermediate",
  3: "Advanced",
  4: "Expert",
};

export function levelLabel(n) {
  return PROFICIENCY_LABELS[n] || `L${n}`;
}
