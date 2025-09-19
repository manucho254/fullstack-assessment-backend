# apps/hos/services.py
from typing import List, Dict, Any
from datetime import datetime
import math

DEFAULT_LIMITS = {
    "maxDrivingHours": 11.0,
    "maxOnDutyHours": 14.0,
    "maxCycleHours": 70.0,
    "requiredRestBreak": 0.5,  # hours
    "requiredOffDuty": 10.0,
}


def calculate_hos_status(
    duty_periods: List[Dict[str, Any]],
    current_cycle_hours: float = 0.0,
    limits: Dict[str, float] = None,
) -> Dict[str, Any]:
    """
    duty_periods: list of dicts with keys: status, start_time (ISO), end_time (ISO)
    returns HOSStatus-like dict
    """
    if limits is None:
        limits = DEFAULT_LIMITS

    driving_hours = 0.0
    on_duty_hours = 0.0
    total_on_duty_time = 0.0
    last_rest_break = 0.0
    violations = []

    for block in duty_periods:
        # parse times (assume ISO or HH:MM) — caller should pass ISO strings
        try:
            start = datetime.fromisoformat(block["start_time"])
            end = datetime.fromisoformat(block["end_time"])
        except Exception:
            # fallback: skip malformed block
            continue
        duration = (end - start).total_seconds() / 3600.0

        if block["status"] == "driving":
            driving_hours += duration
            total_on_duty_time += duration
        elif block["status"] == "on_duty":
            on_duty_hours += duration
            total_on_duty_time += duration
        elif block["status"] in ("off_duty", "sleeper_berth"):
            if duration >= 0.5:
                last_rest_break = total_on_duty_time
            # 10+ hour off duty resets cycles in some rules — left to caller to implement restart logic

    total_on_duty_used = driving_hours + on_duty_hours
    total_cycle_hours = current_cycle_hours + total_on_duty_used

    # driving limit checks
    if driving_hours > limits["maxDrivingHours"]:
        violations.append(
            {
                "type": "daily_drive_limit",
                "severity": "violation",
                "description": f"Exceeded {limits['maxDrivingHours']} driving hours",
            }
        )
    elif driving_hours > limits["maxDrivingHours"] - 1:
        violations.append(
            {
                "type": "approaching_drive_limit",
                "severity": "warning",
                "description": "Approaching driving limit",
            }
        )

    # on duty checks
    if total_on_duty_used > limits["maxOnDutyHours"]:
        violations.append(
            {
                "type": "daily_on_duty_limit",
                "severity": "violation",
                "description": f"Exceeded {limits['maxOnDutyHours']} on-duty hours",
            }
        )
    elif total_on_duty_used > limits["maxOnDutyHours"] - 2:
        violations.append(
            {
                "type": "approaching_on_duty_limit",
                "severity": "warning",
                "description": "Approaching on-duty limit",
            }
        )

    # cycle checks
    if total_cycle_hours > limits["maxCycleHours"]:
        violations.append(
            {
                "type": "cycle_limit",
                "severity": "violation",
                "description": "Exceeded cycle hours",
            }
        )
    elif total_cycle_hours > limits["maxCycleHours"] - 5:
        violations.append(
            {
                "type": "approaching_cycle_limit",
                "severity": "warning",
                "description": "Approaching cycle limit",
            }
        )

    hours_until_break = max(0.0, 8.0 - (total_on_duty_used - last_rest_break))
    hours_until_off_duty = max(0.0, limits["maxOnDutyHours"] - total_on_duty_used)

    return {
        "drivingHoursUsed": driving_hours,
        "onDutyHoursUsed": on_duty_hours,
        "cycleHoursUsed": total_cycle_hours,
        "hoursUntilBreak": hours_until_break,
        "hoursUntilOffDuty": hours_until_off_duty,
        "violations": violations,
        "canContinueDriving": len(
            [v for v in violations if v.get("severity") == "violation"]
        )
        == 0,
    }


def generate_optimized_schedule(
    start_time_iso: str, total_driving_hours: float, current_cycle_hours: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Port of generateOptimizedSchedule - returns DutyBlock-like dicts.
    start_time_iso: ISO timestamp string
    """
    from datetime import datetime, timedelta

    try:
        current_time = datetime.fromisoformat(start_time_iso)
    except Exception:
        current_time = datetime.utcnow().replace(
            hour=6, minute=0, second=0, microsecond=0
        )

    blocks = []
    remaining = total_driving_hours
    block_id = 1

    def add_minutes(t, mins):
        return t + timedelta(minutes=mins)

    # pre-trip 30 min
    blocks.append(
        {
            "id": f"block-{block_id}",
            "status": "on_duty",
            "start_time": current_time.isoformat(),
            "end_time": add_minutes(current_time, 30).isoformat(),
            "remarks": "Pre-trip inspection",
        }
    )
    block_id += 1
    current_time = add_minutes(current_time, 30)

    while remaining > 0:
        drive_time = min(8, remaining)
        drive_minutes = int(drive_time * 60)
        start = current_time
        end = add_minutes(current_time, drive_minutes)
        blocks.append(
            {
                "id": f"block-{block_id}",
                "status": "driving",
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "remarks": f"Driving {drive_time}h",
            }
        )
        block_id += 1
        current_time = end
        remaining -= drive_time

        if remaining > 0:
            # 30 minute break
            start = current_time
            end = add_minutes(current_time, 30)
            blocks.append(
                {
                    "id": f"block-{block_id}",
                    "status": "off_duty",
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                    "remarks": "Required 30-minute break",
                }
            )
            block_id += 1
            current_time = end

    # post trip
    start = current_time
    end = add_minutes(current_time, 30)
    blocks.append(
        {
            "id": f"block-{block_id}",
            "status": "on_duty",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "remarks": "Post-trip inspection",
        }
    )

    return blocks
