# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..exif import Exif


class TestConvertToDegress:
    def test_valid(self):
        value = ((61, 1), (3, 1), (27, 1))
        assert Exif(None, None).convert_to_degress(value) == pytest.approx(61, 0.5)

    def test_invalid(self):
        value = (
            (61, 1),
            (3, 1),
        )
        with pytest.raises(Exif.Invalid):
            Exif(None, None).convert_to_degress(value)


class TestLocate:
    def mock_build_gps_dict(self, mocker, mock_data):
        mocker.patch(
            "social_bfg.common.utils.exif.Exif.build_gps_dict", return_value=mock_data
        )

    def test_ok(self, mocker):
        data = {
            "GPSLatitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLongitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLatitudeRef": "N",
            "GPSLongitudeRef": "E",
        }
        self.mock_build_gps_dict(mocker, data)
        lat, lng = Exif(None, None).locate()
        assert lat == pytest.approx(61, 0.5)
        assert lng == pytest.approx(61, 0.5)

    def test_ok_latitude_ref_south(self, mocker):
        data = {
            "GPSLatitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLongitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLatitudeRef": "S",
            "GPSLongitudeRef": "E",
        }
        self.mock_build_gps_dict(mocker, data)

        lat, lng = Exif(None, None).locate()
        assert lat == pytest.approx(-61, 0.5)
        assert lng == pytest.approx(61, 0.5)

    def test_ok_longitude_ref_west(self, mocker):
        data = {
            "GPSLatitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLongitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLatitudeRef": "N",
            "GPSLongitudeRef": "W",
        }
        self.mock_build_gps_dict(mocker, data)
        lat, lng = Exif(None, None).locate()
        assert lat == pytest.approx(61, 0.5)
        assert lng == pytest.approx(-61, 0.5)

    def test_bad_degress(self, mocker):
        data = {
            "GPSLatitude": ((61, 1), (3, 1),),
            "GPSLongitude": ((61, 1), (3, 1),),
            "GPSLatitudeRef": "N",
            "GPSLongitudeRef": "E",
        }
        self.mock_build_gps_dict(mocker, data)
        with pytest.raises(Exif.Invalid):
            Exif(None, None).locate()
