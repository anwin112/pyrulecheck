def calculate_grades(security_issues: int, quality_issues: int, perf_issues: int):
    # Base score is 10
    security_score = max(0, 10 - (security_issues * 2))  # Critical/Major take 2 points
    quality_score = max(0, 10 - quality_issues)
    maintainability_score = max(0, 10 - perf_issues)
    
    avg_score = (security_score + quality_score + maintainability_score) / 3

    if avg_score >= 9:
        overall_grade = "A"
    elif avg_score >= 7:
        overall_grade = "B"
    elif avg_score >= 5:
        overall_grade = "C"
    elif avg_score >= 3:
        overall_grade = "D"
    else:
        overall_grade = "F"

    return {
        "overall_grade": overall_grade,
        "security_score": security_score,
        "code_quality_score": quality_score,
        "maintainability_score": maintainability_score
    }
