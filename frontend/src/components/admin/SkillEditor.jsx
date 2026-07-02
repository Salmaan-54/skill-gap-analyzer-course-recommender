import React from "react";
import { Plus, Trash2 } from "lucide-react";
import { CATEGORIES } from "../../constants/categories";

const LEVELS = [
  { value: 1, label: "L1 - Beginner" },
  { value: 2, label: "L2 - Intermediate" },
  { value: 3, label: "L3 - Advanced" },
  { value: 4, label: "L4 - Expert" },
];

const emptySkill = () => ({
  skill_name: "",
  required_level: 3,
  category: "",
});

// Controlled editable table of required skills. `skills` is an array of
// { skill_name, required_level, category }. Category is a required dropdown.
export default function SkillEditor({ skills, onChange }) {
  const update = (index, patch) => {
    const next = skills.map((s, i) => (i === index ? { ...s, ...patch } : s));
    onChange(next);
  };

  const addRow = () => onChange([...skills, emptySkill()]);
  const removeRow = (index) => onChange(skills.filter((_, i) => i !== index));

  return (
    <div>
      <div className="table-flush">
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: "42%" }}>
                Skill Name <span className="text-danger">*</span>
              </th>
              <th style={{ width: "22%" }}>
                Required Level <span className="text-danger">*</span>
              </th>
              <th style={{ width: "30%" }}>
                Category <span className="text-danger">*</span>
              </th>
              <th style={{ width: "6%" }} />
            </tr>
          </thead>
          <tbody>
            {skills.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-muted" style={{ textAlign: "center" }}>
                  No skills yet. Add at least one required skill.
                </td>
              </tr>
            ) : (
              skills.map((skill, i) => (
                <tr key={i}>
                  <td>
                    <input
                      className="input"
                      placeholder="e.g. Python"
                      value={skill.skill_name}
                      maxLength={80}
                      onChange={(e) => update(i, { skill_name: e.target.value })}
                    />
                  </td>
                  <td>
                    <select
                      className="select"
                      value={skill.required_level}
                      onChange={(e) =>
                        update(i, { required_level: Number(e.target.value) })
                      }
                    >
                      {LEVELS.map((l) => (
                        <option key={l.value} value={l.value}>
                          {l.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <select
                      className="select"
                      value={skill.category}
                      onChange={(e) => update(i, { category: e.target.value })}
                    >
                      <option value="">Select category...</option>
                      {CATEGORIES.map((c) => (
                        <option key={c.key} value={c.key}>
                          {c.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td style={{ textAlign: "center" }}>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      title="Remove skill"
                      onClick={() => removeRow(i)}
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <button type="button" className="btn btn-secondary btn-sm mt-3" onClick={addRow}>
        <Plus size={15} /> Add skill
      </button>
    </div>
  );
}

export { emptySkill };
