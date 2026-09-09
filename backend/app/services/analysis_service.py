from datetime import datetime

from app import db
from app.models.analysis import Analysis
from app.models.location import Location
from app.services.copernicus_service import CopernicusService
from app.services.vegetation_and_water_index_service import VegetationAndWaterIndexService


class AnalysisService:
    VALID_STATUSES = {"PENDING", "PROCESSING", "COMPLETED", "FAILED"}

    @staticmethod
    def parse_date(value, field_name):
        if not value:
            raise ValueError(f"{field_name} is required")
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(f"{field_name} must use YYYY-MM-DD format") from exc

    @staticmethod
    def validate_analysis_data(data):
        if not data:
            return None, "Request body is required"

        required_fields = ["location_id", "date_from", "date_to", "max_cloud_percentage"]
        for field in required_fields:
            if field not in data:
                return None, f"{field} is required"

        try:
            location_id = int(data["location_id"])
        except (TypeError, ValueError):
            return None, "location_id must be an integer"

        location = db.session.get(Location, location_id)
        if not location:
            return None, "Location not found"

        try:
            date_from = AnalysisService.parse_date(data["date_from"], "date_from")
            date_to = AnalysisService.parse_date(data["date_to"], "date_to")
        except ValueError as exc:
            return None, str(exc)

        if date_from > date_to:
            return None, "date_from must be before or equal to date_to"

        try:
            max_cloud_percentage = float(data["max_cloud_percentage"])
        except (TypeError, ValueError):
            return None, "max_cloud_percentage must be a number"

        if not 0 <= max_cloud_percentage <= 100:
            return None, "max_cloud_percentage must be between 0 and 100"

        return {
            "location": location,
            "date_from": date_from,
            "date_to": date_to,
            "max_cloud_percentage": max_cloud_percentage,
        }, None

    @staticmethod
    def create_analysis(data):
        validated, error = AnalysisService.validate_analysis_data(data)
        if error:
            return None, error, 400

        analysis = Analysis(
            location_id=validated["location"].id,
            date_from=validated["date_from"],
            date_to=validated["date_to"],
            max_cloud_percentage=validated["max_cloud_percentage"],
            status="PROCESSING",
        )
        db.session.add(analysis)
        db.session.commit()

        try:
            bands = CopernicusService().get_sentinel2_bands(
                validated["location"],
                validated["date_from"],
                validated["date_to"],
                validated["max_cloud_percentage"],
            )
            ndvi = VegetationIndexService.calculate_ndvi(bands["B04"], bands["B08"])
            ndwi = VegetationIndexService.calculate_ndwi(bands["B03"], bands["B08"])

            analysis.mean_ndvi = VegetationIndexService.mean_index(ndvi)
            analysis.mean_ndwi = VegetationIndexService.mean_index(ndwi)
            analysis.satellite_date = bands.get("satellite_date")
            analysis.status = "COMPLETED"
        except Exception:
            analysis.status = "FAILED"

        db.session.commit()
        return analysis, None, 201

    @staticmethod
    def get_filtered_analyses(args):
        query = Analysis.query

        if args.get("location_id"):
            query = query.filter(Analysis.location_id == int(args["location_id"]))
        if args.get("status"):
            status = args["status"].upper()
            if status in AnalysisService.VALID_STATUSES:
                query = query.filter(Analysis.status == status)
        if args.get("date_from"):
            query = query.filter(Analysis.date_from >= AnalysisService.parse_date(args["date_from"], "date_from"))
        if args.get("date_to"):
            query = query.filter(Analysis.date_to <= AnalysisService.parse_date(args["date_to"], "date_to"))

        return query.order_by(Analysis.created_at.desc()).all()
