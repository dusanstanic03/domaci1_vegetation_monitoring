from flask import Blueprint, request

from app import db
from app.models.location import Location
from app.services.location_service import LocationService


location_bp = Blueprint("locations", __name__, url_prefix="/api/locations")


@location_bp.post("")
def create_location():
    location, error = LocationService.create_location(request.get_json(silent=True))
    if error:
        return {"error": error}, 400

    return location.to_dict(), 201


@location_bp.get("")
def get_locations():
    locations = Location.query.order_by(Location.created_at.desc()).all()
    return {"items": [location.to_dict() for location in locations]}, 200


@location_bp.get("/<int:location_id>")
def get_location(location_id):
    location = db.session.get(Location, location_id)
    if not location:
        return {"error": "Location not found"}, 404

    return location.to_dict(), 200


@location_bp.put("/<int:location_id>")
def update_location(location_id):
    location = db.session.get(Location, location_id)
    if not location:
        return {"error": "Location not found"}, 404

    location, error = LocationService.update_location(location, request.get_json(silent=True))
    if error:
        return {"error": error}, 400

    return location.to_dict(), 200


@location_bp.delete("/<int:location_id>")
def delete_location(location_id):
    location = db.session.get(Location, location_id)
    if not location:
        return {"error": "Location not found"}, 404

    db.session.delete(location)
    db.session.commit()
    return "", 204
