# apps/trips/services.py
import math
import requests
from typing import List, Dict, Any, Tuple

from django.conf import settings

# Keep constants easy to tune
AVG_SPEED_MPH = 55.0
FUEL_INTERVAL_MILES = 400  # frontend uses 400 as example
MAX_DRIVE_BEFORE_BREAK_HOURS = 8.0


# Simple wrapper for geocoding using Nominatim (OpenStreetMap)
def geocode_address(address: str, countrycodes: str = "us") -> Tuple[float, float]:
    """
    Returns (lat, lon) or raises ValueError on failure.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "q": address, "limit": 1, "countrycodes": countrycodes}
    try:
        resp = requests.get(
            url, params=params, timeout=6, headers={"User-Agent": "hos-app/1.0"}
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            raise ValueError("No geocode result")
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        # Bubble error to caller — caller may fallback to simple parsing
        raise


def haversine_miles(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    # a = (lat, lon)
    R = 3959.0  # miles
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    hav = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(hav), math.sqrt(1 - hav))
    return R * c


def calculate_approx_route(coords: List[Tuple[float, float]]) -> Dict[str, Any]:
    """
    Simple approximated route: straight-line segments, returns
    path (list of points), distance (miles), duration (hours).
    This is a fallback if you don't use a routing engine.
    """
    path = []
    total_distance = 0.0
    total_duration_hours = 0.0
    for i in range(len(coords) - 1):
        s = coords[i]
        e = coords[i + 1]
        total_distance += haversine_miles(s, e)
        duration = haversine_miles(s, e) / AVG_SPEED_MPH
        total_duration_hours += duration
        # simple interpolation for visualization (n points)
        steps = max(2, int(max(1, math.floor(haversine_miles(s, e) / 50))))
        for step in range(steps + 1):
            ratio = step / steps
            path.append((s[0] + (e[0] - s[0]) * ratio, s[1] + (e[1] - s[1]) * ratio))
    return {"path": path, "distance": total_distance, "duration": total_duration_hours}


def generate_hos_waypoints(
    origin: Tuple[float, float],
    pickup: Tuple[float, float],
    dropoff: Tuple[float, float],
    hos_status: Dict[str, Any],
    route_distance: float,
) -> List[Dict[str, Any]]:
    """
    Port of the frontend generateHOSWaypoints logic to Python.
    Returns list of waypoints with lat/lon, type, eta_str, reason if any.
    """
    waypoints = []

    # start time: allow the caller to send a starting timestamp in hos_status if needed.
    # For demo use local naive datetime at 06:00
    from datetime import datetime, timedelta

    current_time = datetime.utcnow().replace(hour=6, minute=0, second=0, microsecond=0)

    # origin
    waypoints.append(
        {
            "coordinates": origin,
            "type": "origin",
            "address": "Starting location",
            "eta": current_time,
            "complianceStatus": "safe",
        }
    )

    # pickup leg
    dist_to_pickup = haversine_miles(origin, pickup)
    time_to_pickup_hours = dist_to_pickup / AVG_SPEED_MPH
    current_time += timedelta(hours=time_to_pickup_hours)
    waypoints.append(
        {
            "coordinates": pickup,
            "type": "pickup",
            "address": "Pickup location",
            "eta": current_time,
            "serviceWindow": "1 hour",
            "complianceStatus": "safe",
        }
    )
    # add 1 hour service
    current_time += timedelta(hours=1.0)

    # iterate between pickup and dropoff placing fuel and rest stops
    remaining_distance = haversine_miles(pickup, dropoff)
    distance_covered = 0.0
    driving_time_since_break = hos_status.get("drivingHoursUsed", 0.0)
    next_fuel_at = FUEL_INTERVAL_MILES

    def interp_point(ratio):
        return (
            pickup[0] + (dropoff[0] - pickup[0]) * ratio,
            pickup[1] + (dropoff[1] - pickup[1]) * ratio,
        )

    while distance_covered < remaining_distance - 1e-6:
        remaining = remaining_distance - distance_covered
        hours_until_break = max(
            0.0, MAX_DRIVE_BEFORE_BREAK_HOURS - driving_time_since_break
        )
        miles_until_break = hours_until_break * AVG_SPEED_MPH
        next_chunk = min(
            remaining, miles_until_break if miles_until_break > 0 else remaining
        )
        # fuel consideration
        if (
            next_fuel_at - distance_covered > 0
            and next_fuel_at - distance_covered < next_chunk
        ):
            next_chunk = next_fuel_at - distance_covered
        if next_chunk <= 1e-6:
            break
        distance_covered += next_chunk
        ratio = min(1.0, distance_covered / remaining_distance)
        new_pos = interp_point(ratio)

        current_time += timedelta(hours=(next_chunk / AVG_SPEED_MPH))
        driving_time_since_break += next_chunk / AVG_SPEED_MPH

        # fuel stop
        if (
            abs(distance_covered - next_fuel_at) < 1e-3
            or distance_covered > next_fuel_at - 1e-3
        ):
            waypoints.append(
                {
                    "coordinates": new_pos,
                    "type": "fuel_stop",
                    "address": "Fuel stop",
                    "eta": current_time,
                    "reason": "Recommended fuel stop",
                    "complianceStatus": "safe",
                }
            )
            current_time += timedelta(minutes=15)
            next_fuel_at += FUEL_INTERVAL_MILES

        # rest break
        if (
            driving_time_since_break >= MAX_DRIVE_BEFORE_BREAK_HOURS
            or hos_status.get("drivingHoursUsed", 0) + driving_time_since_break
            >= MAX_DRIVE_BEFORE_BREAK_HOURS
        ):
            waypoints.append(
                {
                    "coordinates": new_pos,
                    "type": "rest_break",
                    "address": "Required rest break",
                    "eta": current_time,
                    "reason": "HOS 8-hour driving limit",
                    "complianceStatus": "safe",
                }
            )
            current_time += timedelta(minutes=30)
            driving_time_since_break = 0.0

    # final dropoff
    last_leg_distance = haversine_miles(
        (
            interp_point(min(1.0, distance_covered / remaining_distance))
            if remaining_distance > 0
            else pickup
        ),
        dropoff,
    )
    if last_leg_distance > 0.001:
        current_time += timedelta(hours=(last_leg_distance / AVG_SPEED_MPH))

    waypoints.append(
        {
            "coordinates": dropoff,
            "type": "dropoff",
            "address": "Drop-off location",
            "eta": current_time,
            "serviceWindow": "1 hour",
            "complianceStatus": (
                "safe" if hos_status.get("canContinueDriving", True) else "violation"
            ),
        }
    )

    return waypoints


from typing import List, Dict, Any, Tuple, Union
from datetime import datetime


def build_route_response(
    waypoints: List[Dict[str, Any]],
    path: List[Tuple[float, float]],
    distance: float,
    duration: float,
) -> Dict[str, Any]:
    """
    Build RouteCalculationResponse-style dict.

    Returns:
        Dict[str, Any]: A response dictionary containing route,
                        HOS schedule, and compliance warnings.
    """
    route_coords: List[List[float]] = [[p[0], p[1]] for p in path]
    route_waypoints: List[Dict[str, Union[str, int, float, Dict[str, float]]]] = []

    for i, wp in enumerate(waypoints):
        eta: Union[datetime, str, None] = wp.get("eta")
        eta_str: str = eta.isoformat() if isinstance(eta, datetime) else str(eta)

        route_waypoints.append(
            {
                "id": str(i + 1),
                "type": wp.get("type", ""),
                "location": {
                    "lat": float(wp["coordinates"][0]),
                    "lon": float(wp["coordinates"][1]),
                },
                "coordinates": [
                    float(wp["coordinates"][0]),
                    float(wp["coordinates"][1]),
                ],
                "estimated_arrival": eta_str,
                "duration_minutes": int(wp.get("duration_minutes", 0)),
                "description": str(wp.get("reason") or wp.get("address", "")),
                "is_mandatory": wp.get("type") in ("rest_break", "mandatory_break"),
            }
        )

    return {
        "route": {
            "coordinates": route_coords,
            "distance": distance,
            "duration": duration,
            "waypoints": route_waypoints,
        },
        "hos_schedule": [],  # can be added later
        "compliance_warnings": [],  # can be added later
    }
