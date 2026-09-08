from app import db
from app.models.location import Location


class LocationService:
    @staticmethod
    def validate_location_data(data):
        if not data:
            return "Request body is required"

        required_fields = ["name", "min_lat", "min_lon", "max_lat", "max_lon"]
        for field in required_fields:
            if field not in data:
                return f"{field} is required"

        if not str(data["name"]).strip():
            return "name must not be empty"

        try:
            min_lat = float(data["min_lat"])
            min_lon = float(data["min_lon"])
            max_lat = float(data["max_lat"])
            max_lon = float(data["max_lon"])
        except (TypeError, ValueError):
            return "coordinates must be numbers"

        if not -90 <= min_lat <= 90 or not -90 <= max_lat <= 90:
            return "latitude must be between -90 and 90"
        if not -180 <= min_lon <= 180 or not -180 <= max_lon <= 180:
            return "longitude must be between -180 and 180"
        if min_lat >= max_lat:
            return "min_lat must be less than max_lat"
        if min_lon >= max_lon:
            return "min_lon must be less than max_lon"

        return None

    @staticmethod
    def create_location(data):
        error = LocationService.validate_location_data(data)
        if error:
            return None, error

        location = Location(
            name=data["name"].strip(),
            min_lat=float(data["min_lat"]),
            min_lon=float(data["min_lon"]),
            max_lat=float(data["max_lat"]),
            max_lon=float(data["max_lon"]),
        )
        db.session.add(location)
        db.session.commit()
        return location, None

    @staticmethod
    def update_location(location, data):
        error = LocationService.validate_location_data(data)
        if error:
            return None, error

        location.name = data["name"].strip()
        location.min_lat = float(data["min_lat"])
        location.min_lon = float(data["min_lon"])
        location.max_lat = float(data["max_lat"])
        location.max_lon = float(data["max_lon"])
        db.session.commit()
        return location, None
