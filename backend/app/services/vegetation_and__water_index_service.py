import numpy as np


class VegetationAndWaterIndexService:
    @staticmethod
    def calculate_ndvi(red, nir):
        red = np.asarray(red, dtype=float)
        nir = np.asarray(nir, dtype=float)
        denominator = nir + red

        return np.divide(nir - red, denominator, out=np.zeros_like(denominator), where=denominator != 0)

    @staticmethod
    def calculate_ndwi(green, nir):
        green = np.asarray(green, dtype=float)
        nir = np.asarray(nir, dtype=float)
        denominator = green + nir

        return np.divide(green - nir, denominator, out=np.zeros_like(denominator), where=denominator != 0)

    @staticmethod
    def mean_index(index_values):
        return float(np.nanmean(index_values))
