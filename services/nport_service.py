import httpx
import xmltodict

from .cache_service import CacheService

class NportService:
    def __init__(self):
        self.headers = {
            "User-Agent": "NPORT API contact js-nport@example.com",
            "Accept-Encoding": "gzip, deflate",
        }
        self.cache = CacheService()

    async def get_latest_nport(self, cik: str):
    
            cik = cik.zfill(10)
    
            latest_filing = await self.get_latest_filing(cik)
    
            if latest_filing is None:
                return None
    
            filing_xml = await self.fetch_filing_xml(
                cik,
                latest_filing["accession"]
            )
    
            filing_data = xmltodict.parse(filing_xml)

            return self.build_nport_response(cik, latest_filing, filing_data)

    def build_nport_response(self, cik: str, filing: dict, filing_data: dict):

        form_data = filing_data["edgarSubmission"]["formData"]

        gen_info = form_data["genInfo"]
        fund_info = form_data["fundInfo"]

        holdings = form_data["invstOrSecs"]["invstOrSec"]

        if isinstance(holdings, dict):
            holdings = [holdings]

        return {
            "cik": cik,
            "filing": {
                "form": filing["form"],
                "filing_date": filing["filing_date"],
                "report_date": filing["report_date"]
            },
            "form_data": {
                "gen_info": {
                    "reg_name": gen_info["regName"]
                },
                "fund_info": {
                    "total_assets": fund_info["totAssets"],
                    "total_liabilities": fund_info["totLiabs"],
                    "net_assets": fund_info["netAssets"]
                },
                "holdings": [
                    {
                        "cusip": self.get_cusip(holding),
                        "isin": holding.get("identifiers", {}).get("isin", {}).get("@value"),
                        "lei": holding.get("lei"),
                        "name":  self.clean_value(holding.get("name")) or self.clean_value(holding.get("title")),
                        "balance": holding.get("balance"),
                        "value": holding.get("valUSD"),
                        "pctVal": holding.get("pctVal"),
                        "assetCat": holding.get("assetCat"),
                        "issuerCat": self.clean_value(
                            holding.get("issuerCat") or
                            holding.get("issuerConditional", {}).get("@issuerCat")
                        ),
                        "fairValLevel": holding.get("fairValLevel"),
                        "payoffProfile": holding.get("payoffProfile"),
                        "invCountry": holding.get("invCountry"),
                    }
                    for holding in holdings
                ]
            }
        }

    def clean_value(self, value):
        if value in [None, "", "N/A"]:
            return None

        return value

    def get_cusip(self, holding: dict):
        cusip = holding.get("cusip")

        if cusip and cusip not in ["N/A", "000000000"]:
            return cusip

        derivative_info = holding.get("derivativeInfo", {})
        swap_deriv = derivative_info.get("swapDeriv", {})
        ref_instrument = swap_deriv.get("descRefInstrmnt", {})
        other_ref = ref_instrument.get("otherRefInst", {})
        identifiers = other_ref.get("identifiers", {})
        nested_cusip = identifiers.get("cusip", {}).get("@value")

        if nested_cusip:
            return nested_cusip

        return None
    
    async def get_latest_filing(self, cik: str):
        cache_key = f"latest:{cik}"

        latest_filing = self.cache.get(cache_key)

        if latest_filing is not None:
            return latest_filing

        filings = await self.fetch_filing_history(cik)

        latest_filing = self.find_latest_filing(filings)

        if latest_filing is not None:
            self.cache.set(
                cache_key,
                latest_filing,
                # 12 hours
                expire=43200
            )

        return latest_filing

    async def fetch_filing_history(self, cik: str):
        submissions_url = (
            f"https://data.sec.gov/submissions/CIK{cik}.json"
        )

        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(
                    submissions_url,
                    timeout=30
                )
                response.raise_for_status()

                return response.json()

            except httpx.HTTPStatusError as exc:

                if exc.response.status_code == 404:
                    raise RuntimeError(
                        f"No SEC submissions record was found for CIK {cik}."
                    )

                raise RuntimeError(
                    f"The SEC submissions service returned "
                    f"HTTP {exc.response.status_code}."
                )

    def find_latest_filing(self, submissions: dict):
        filings = submissions["filings"]["recent"]

        results = []

        for i, form in enumerate(filings["form"]):

            if form in ["NPORT-P", "NPORT-P/A"]:

                results.append({
                    "form": form,
                    "filing_date": filings["filingDate"][i],
                    "report_date": filings["reportDate"][i],
                    "accession": filings["accessionNumber"][i],
                    "document": filings["primaryDocument"][i]
                })

        return results[0] if results else None

    async def fetch_filing_xml(self, cik: str, accession: str):
        cache_key = f"filing:{accession}"
        cached_xml = self.cache.get(cache_key)

        if cached_xml is not None:
            return cached_xml

        accession_clean = accession.replace("-", "")

        filing_url = (
            f"https://www.sec.gov/Archives/edgar/data/"
            f"{cik.lstrip('0')}/{accession_clean}/primary_doc.xml"
        )

        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(filing_url)
            response.raise_for_status()

            filing_xml = response.content

        self.cache.set(cache_key, filing_xml)

        return filing_xml
