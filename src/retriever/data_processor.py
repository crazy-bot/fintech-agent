def process_cap_table(company_info: dict, table_name: str, table_data: dict, table_title: str) -> tuple[str, dict]:
    """
    Processes the capitalization table into a clean Markdown table format.
    
    Args:
        company_info (dict): Information about the company.
        table_data (dict): The data for the capitalization table.
        table_name (str): The name of the capitalization table.
        table_title (str): The human-readable title for the table.

    Returns:
        tuple[str, dict]: The processed content and metadata.
    """
    company_name = company_info['name']
    as_of_date = table_data.get("as_of", "N/A")
    
    keywords = []
    
    # --- Generate Content ---
    content_parts = [
        f"## {table_title} for {company_name} (as of {as_of_date})",
        f"This document contains the capitalization table for {company_name}, detailing its debt structure.",
    ]
    
    # Create Markdown table headers
    headers = "| Instrument Name | Security | Maturity | Rate | Amount (USDm) |\n|---|---|---|---|---|"
    md_rows = [headers]
    
    for row in table_data.get("rows", []):
        instrument_name = row.get("name", "N/A")
        amount_val = row.get('amount_usdm')
        
        # Default display for amount, handling None values gracefully
        amount_display = str(amount_val) if amount_val is not None else ""

        # Emphasize subtotals with bold formatting
        if row.get("subtotal"):
            instrument_name = f"**{instrument_name}**"
            amount_display = f"**{amount_display}**"
        
        # Use .get with a default of '' to avoid printing 'None' for empty cells
        security = row.get('security', '')
        maturity = row.get('maturity', '')
        rate = row.get('rate', '')

        md_rows.append(f"| {instrument_name} | {security} | {maturity} | {rate} | {amount_display} |")

    content_parts.append("\n".join(md_rows))
    content = "\n\n".join(content_parts)

    # --- Generate Metadata ---
    # This structure is consistent with the financial_table processor
    metadata = {
        "company_name": company_name,
        "company_id": company_info['id'],
        "table_name": table_name,
        "keywords": keywords,
        "source_url": f"www.9fin.com{table_data.get('url', '')}"
    }
    
    return content, metadata


def process_financial_table(company_info: dict, table_name: str, table_data: dict, table_title: str) -> tuple[str, dict]:
    """
    Processes financial tables like 'key_financials' and 'cash_flow_and_leverage'.
    
    Args:
        company_info (dict): Information about the company.
        table_data (dict): The data for the financial table.
        table_name (str): The name of the financial table.
        table_meta (dict): Metadata for the financial table.

    Returns:
        tuple[str, dict]: The processed content and metadata.
    """
    company_name = company_info['name']
    currency = company_info['currency']
    periods = company_info['periods']
    
    keywords = [row.get("metric", "") for row in table_data.get("rows", []) if row.get("metric")]
    
    # --- Generate Content ---
    content_parts = [
        f"## {table_title} for {company_name} (Currency: {currency})",
        f"This document contains data on: {', '.join(keywords)}.",
        "\n### Data"
    ]
    
    for row in table_data.get("rows", []):
        metric = row.get("metric", "N/A")
        unit = row.get("unit", "")
        values = row.get("values", [])
        
        content_parts.append(f"- **{metric}**:")
        
        for i, value in enumerate(values):
            if i < len(periods):
                period_info = periods[i]
                period_str = f"{period_info.get('period')} ({period_info.get('date')})"
                value_str = f"{value} {unit}"
                content_parts.append(f"  - {period_str}: {value_str}")

    content = "\n".join(content_parts)
    metadata = {
        "company_name": company_name,
        "company_id": company_info['id'],
        "table_name": table_name,
        "keywords": keywords,
        "source_url": f"www.9fin.com{table_data.get('url', '')}",
        "currency": currency
    }
    return content, metadata