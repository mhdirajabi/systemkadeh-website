import os
import tarfile
import urllib.request
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Downloads and extracts GeoLite2 databases"

    def handle(self, *args, **options):
        os.makedirs(settings.GEOIP_PATH, exist_ok=True)

        # Get your MaxMind license key from:
        # https://support.maxmind.com/account-faq/account-related/how-do-i-generate-a-license-key/
        license_key = os.getenv("MAXMIND_LICENSE_KEY")

        if not license_key:
            self.stdout.write(
                self.style.ERROR("MAXMIND_LICENSE_KEY not set in environment")
            )
            return

        urls = [
            f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key={license_key}&suffix=tar.gz",
            f"https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country&license_key={license_key}&suffix=tar.gz",
        ]

        for url in urls:
            try:
                filename = url.split("edition_id=")[1].split("&")[0] + ".tar.gz"
                filepath = os.path.join(settings.GEOIP_PATH, filename)

                self.stdout.write(f"Downloading {filename}...")
                urllib.request.urlretrieve(url, filepath)

                self.stdout.write(f"Extracting {filename}...")
                with tarfile.open(filepath, "r:gz") as tar:
                    for member in tar.getmembers():
                        if member.name.endswith(".mmdb"):
                            member.name = os.path.basename(member.name)
                            tar.extract(member, settings.GEOIP_PATH)

                os.remove(filepath)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated {filename.split(".")[0]}')
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {url}: {str(e)}"))
