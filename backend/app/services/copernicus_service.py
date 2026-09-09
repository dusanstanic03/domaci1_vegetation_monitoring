import numpy as np
from flask import current_app
from sentinelhub import (
    BBox,
    CRS,
    DataCollection,
    MimeType,
    SHConfig,
    SentinelHubRequest,
    bbox_to_dimensions,
)


class CopernicusService:
    EVALSCRIPT = """
    //VERSION=3
    function setup() {
        return {
            input: ["B03", "B04", "B08", "dataMask"],
            output: { bands: 4, sampleType: "FLOAT32" }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B03, sample.B04, sample.B08, sample.dataMask];
    }
    """

    def __init__(self):
        self.config = SHConfig()
        self.config.sh_client_id = current_app.config["COPERNICUS_CLIENT_ID"]
        self.config.sh_client_secret = current_app.config["COPERNICUS_CLIENT_SECRET"]
        self.config.sh_base_url = current_app.config["COPERNICUS_BASE_URL"]
        self.config.sh_token_url = current_app.config["COPERNICUS_TOKEN_URL"]

    def get_sentinel2_bands(self, location, date_from, date_to, max_cloud_percentage):
        if not self.config.sh_client_id or not self.config.sh_client_secret:
            raise ValueError("Copernicus credentials are not configured")

        bbox = BBox(
            bbox=[location.min_lon, location.min_lat, location.max_lon, location.max_lat],
            crs=CRS.WGS84,
        )
        size = bbox_to_dimensions(bbox, resolution=10)

        request = SentinelHubRequest(
            evalscript=self.EVALSCRIPT,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A.define_from(
                        "s2l2a-cdse", service_url=current_app.config["COPERNICUS_BASE_URL"]
                    ),
                    time_interval=(date_from.isoformat(), date_to.isoformat()),
                    maxcc=max_cloud_percentage / 100,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=self.config,
        )

        data = request.get_data()
        if not data:
            raise ValueError("Copernicus did not return Sentinel-2 data")

        image = np.asarray(data[0])
        mask = image[:, :, 3] == 1

        return {
            "B03": np.where(mask, image[:, :, 0], np.nan),
            "B04": np.where(mask, image[:, :, 1], np.nan),
            "B08": np.where(mask, image[:, :, 2], np.nan),
            "satellite_date": date_from,
        }
