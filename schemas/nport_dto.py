
from pydantic import BaseModel


class FilingDTO(BaseModel):
    form: str
    filing_date: str
    report_date: str


class GeneralInfoDTO(BaseModel):
    reg_name: str


class FundInfoDTO(BaseModel):
    total_assets: str
    total_liabilities: str
    net_assets: str


class HoldingDTO(BaseModel):
    cusip: str | None = None
    name: str | None = None
    balance: str | None = None
    value: str | None = None


class FormDataDTO(BaseModel):
    gen_info: GeneralInfoDTO
    fund_info: FundInfoDTO
    holdings: list[HoldingDTO]


class NportResponseDTO(BaseModel):
    cik: str
    filing: FilingDTO
    form_data: FormDataDTO
