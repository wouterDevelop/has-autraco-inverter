"""Models for Autarco."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Inverter:
    """Object representing an Inverter model response from the API."""

    serial_number: str | None
    out_ac_power: int | None
    out_ac_energy_total: int | None
    grid_turned_off: bool | None
    health: str | None

    @classmethod
    def from_json(cls, data: dict[str | int, Any]) -> Inverter:
        """Create an Inverter object from a JSON response.

        Args:
            data: JSON response from the API.

        Returns:
            An Inverter object.
        """
        data = data[1]
        return cls(
            serial_number=data.get("sn"),
            out_ac_power=data.get("out_ac_power"),
            out_ac_energy_total=data.get("out_ac_energy_total"),
            grid_turned_off=data.get("grid_turned_off"),
            health=data.get("health"),
        )


@dataclass
class Solar:
    """Object representing a Solar model response from the API."""

    power_production: int | None
    energy_production_today: int | None
    energy_production_month: int | None
    energy_production_total: int | None

    @staticmethod
    def from_json(data: dict[str, Any],dataPower: dict[str, Any]) -> Solar:
        """Create an Solar object from a JSON response.

        Args:
            data: JSON response from the API.

        Returns:
            An Solar object.
        """
        data = data['stats']['kpis']
        dataPower = dataPower['stats']['kpis']
        return Solar(
            power_production=dataPower.get("pv_now"),
            energy_production_today=data.get("pv_today"),
            energy_production_month=data.get("pv_month"),
            energy_production_total=data.get("pv_to_date"),
        )


@dataclass
class Account:
    """Object representing an Account model response from the API."""

    public_key: str | None
    name: str | None
    city: str | None
    country: str | None
    @staticmethod
    def from_json(data: dict[str, Any]) -> Account:
        """Create an Account object from a JSON response.

        Args:
            data: JSON response from the API.

        Returns:
            An Account object.
        """

        return Account(
            public_key=data.get("public_key"),
            name=data.get("name"),
            city=data.get("city"),
            country=data.get("country"),
        )
