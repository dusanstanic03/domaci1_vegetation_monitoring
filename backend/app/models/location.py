from datetime import datetime, timezone

from app import db


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    min_lat = db.Column(db.Float, nullable=False)
    min_lon = db.Column(db.Float, nullable=False)
    max_lat = db.Column(db.Float, nullable=False)
    max_lon = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    analyses = db.relationship(
        "Analysis", back_populates="location", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "min_lat": self.min_lat,
            "min_lon": self.min_lon,
            "max_lat": self.max_lat,
            "max_lon": self.max_lon,
            "created_at": self.created_at.isoformat(),
        }
