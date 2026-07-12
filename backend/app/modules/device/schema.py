from pydantic import BaseModel
from typing import Optional


class DeviceInfo(BaseModel):
    device_name: str = "Laptop (Prototype)"
    platform: str = "Windows"
    camera_available: bool = True
    microphone_available: bool = True


class DeviceStatusResponse(BaseModel):
    active_connections: int
    device_info: DeviceInfo
    uptime_ok: bool
