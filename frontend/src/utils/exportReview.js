import * as XLSX from "xlsx";

/**
 * Export a single review analysis result to an .xlsx file.
 * Creates a well-structured workbook with employee info, ratings, skills, and recommendations.
 */
export function exportReviewToXlsx(review) {
  const wb = XLSX.utils.book_new();

  // --- Sheet 1: Overview ---
  const overviewData = [
    ["Employee Review Analysis Report"],
    [],
    ["Employee Name", review.employee_name],
    ["Department", review.department],
    ["Created By", review.created_by || "N/A"],
    ["Date", new Date(review.created_at).toLocaleString()],
    [],
    ["Sentiment", review.sentiment || "N/A"],
    [
      "Sentiment Confidence",
      review.sentiment_confidence != null
        ? `${(review.sentiment_confidence * 100).toFixed(1)}%`
        : "N/A",
    ],
    [],
    ["Behavioral Rating", review.behavioral_rating != null ? `${review.behavioral_rating}/5` : "N/A"],
    ["Performance Rating", review.performance_rating != null ? `${review.performance_rating}/5` : "N/A"],
    [],
    ["Review Text"],
    [review.review_text || ""],
  ];

  const wsOverview = XLSX.utils.aoa_to_sheet(overviewData);

  // Set column widths for readability
  wsOverview["!cols"] = [{ wch: 24 }, { wch: 60 }];

  XLSX.utils.book_append_sheet(wb, wsOverview, "Overview");

  // --- Sheet 2: Skills ---
  const skillsData = [["Skills & Gaps Analysis"], []];

  skillsData.push(["Skills Identified", "Skill Gaps"]);

  const skillsFound = review.skills_found || [];
  const skillGaps = review.skill_gaps || [];
  const maxRows = Math.max(skillsFound.length, skillGaps.length, 1);

  for (let i = 0; i < maxRows; i++) {
    skillsData.push([skillsFound[i] || "", skillGaps[i] || ""]);
  }

  const wsSkills = XLSX.utils.aoa_to_sheet(skillsData);
  wsSkills["!cols"] = [{ wch: 30 }, { wch: 30 }];
  XLSX.utils.book_append_sheet(wb, wsSkills, "Skills");

  // --- Sheet 3: Recommendations ---
  const recsData = [["Recommendations"], []];

  if (review.recommendations) {
    // Split bullet-pointed recommendations into separate rows
    const lines = review.recommendations
      .split(/\*\s+/)
      .filter((line) => line.trim() !== "");
    lines.forEach((line) => {
      recsData.push([`• ${line.trim()}`]);
    });
  } else {
    recsData.push(["No recommendations available."]);
  }

  const wsRecs = XLSX.utils.aoa_to_sheet(recsData);
  wsRecs["!cols"] = [{ wch: 80 }];
  XLSX.utils.book_append_sheet(wb, wsRecs, "Recommendations");

  // Generate filename and download
  const safeName = review.employee_name.replace(/[^a-zA-Z0-9]/g, "_");
  const dateStr = new Date(review.created_at)
    .toISOString()
    .slice(0, 10)
    .replace(/-/g, "");
  const filename = `Review_${safeName}_${dateStr}.xlsx`;

  XLSX.writeFile(wb, filename);
}
