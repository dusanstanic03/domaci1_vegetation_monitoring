from flask import Blueprint, request

from app import db
from app.models.analysis import Analysis
from app.services.analysis_service import AnalysisService


analysis_bp = Blueprint("analyses", __name__, url_prefix="/api/analyses")


@analysis_bp.post("")
def create_analysis():
    analysis, error, status_code = AnalysisService.create_analysis(request.get_json(silent=True))
    if error:
        return {"error": error}, status_code

    return analysis.to_dict(), status_code


@analysis_bp.get("")
def get_analyses():
    try:
        analyses = AnalysisService.get_filtered_analyses(request.args)
    except ValueError as exc:
        return {"error": str(exc)}, 400

    return {"items": [analysis.to_dict() for analysis in analyses]}, 200


@analysis_bp.get("/<int:analysis_id>")
def get_analysis(analysis_id):
    analysis = db.session.get(Analysis, analysis_id)
    if not analysis:
        return {"error": "Analysis not found"}, 404

    return analysis.to_dict(), 200


@analysis_bp.delete("/<int:analysis_id>")
def delete_analysis(analysis_id):
    analysis = db.session.get(Analysis, analysis_id)
    if not analysis:
        return {"error": "Analysis not found"}, 404

    db.session.delete(analysis)
    db.session.commit()
    return "", 204
