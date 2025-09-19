from apps.utils.base import BaseModel


from django.db import models


class ComplianceReport(BaseModel):
    """
    Model to store compliance reports for drivers and vehicles.
    """

    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.CASCADE, related_name="compliance_reports"
    )
    driver = models.ForeignKey(
        "drivers.Driver", on_delete=models.CASCADE, related_name="compliance_reports"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    total_violations = models.IntegerField(default=0)
    violations_by_type = models.JSONField(
        default=dict
    )  # e.g., {"speeding": 3, "harsh_braking": 1}
    driver_compliance_scores = models.JSONField(
        default=dict
    )  # e.g., {"safety_score": 85, "efficiency_score": 90}

    def __str__(self):
        return f"Compliance Report for {self.driver} - {self.vehicle} ({self.period_start} to {self.period_end})"
