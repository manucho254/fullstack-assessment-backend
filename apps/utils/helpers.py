def _aggregate_violations_by_type(reports):
    """
    Combine violations_by_type JSON fields across reports.
    """
    aggregated = {}
    for report in reports:
        for v_type, count in report.violations_by_type.items():
            aggregated[v_type] = aggregated.get(v_type, 0) + count
    return aggregated


def _average_driver_scores(reports):
    """
    Compute average scores from driver_compliance_scores JSON field.
    """
    if not reports.exists():
        return {}

    totals = {}
    counts = {}

    for report in reports:
        for metric, score in report.driver_compliance_scores.items():
            totals[metric] = totals.get(metric, 0) + score
            counts[metric] = counts.get(metric, 0) + 1

    return {metric: round(totals[metric] / counts[metric], 2) for metric in totals}
