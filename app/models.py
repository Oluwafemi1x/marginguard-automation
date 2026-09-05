from pydantic import BaseModel, HttpUrl


class WatchItem(BaseModel):
    sku: str
    product_name: str
    our_price: float
    competitor: str
    url: HttpUrl


class ScanRequest(BaseModel):
    items: list[WatchItem]
