from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import cache
from django.conf import settings
import os


class GeoIPService:
    def __init__(self):
        self.geoip = GeoIP2(
            country=os.path.join(settings.GEOIP_PATH, settings.GEOIP_COUNTRY),
            city=os.path.join(settings.GEOIP_PATH, settings.GEOIP_CITY),
        )

    def get_location(self, ip_address):
        cache_key = f"geoip_{ip_address}"
        if cached := cache.get(cache_key):
            return cached
        else:
            result = self._geoip_lookup(ip_address)
            cache.set(cache_key, result, timeout=86400)  # Cache for 24 hours
            return result

    def _geoip_lookup(self, ip_address):
        try:
            if ip_address == "127.0.0.1":
                return {"city": "Local", "country": "Development"}

            city_info = self.geoip.city(ip_address)

            return {
                "city": city_info.get("city", {})
                .get("names", {})
                .get(
                    "fa",
                    city_info.get("city", {}).get("names", {}).get("en", "Unknown"),
                ),
                "country": city_info.get("country", {})
                .get("names", {})
                .get(
                    "fa",
                    city_info.get("country", {}).get("names", {}).get("en", "Unknown"),
                ),
            }
        except Exception:
            return {"city": "Unknown", "country": "Unknown"}


geoip_service = GeoIPService()
