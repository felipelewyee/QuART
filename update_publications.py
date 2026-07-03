import requests
import yaml

ORCID_ID = "0000-0002-3908-3144"
URL = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"

try:
    response = requests.get(URL, headers={"Accept": "application/json"}, timeout=10)
    if response.status_code == 200:
        data = response.json()
        publications = []

        for work in data.get("group", []):
            work_summary = work.get("work-summary", [{}])[0]
            
            title = work_summary.get("title", {}).get("title", {}).get("value", "Sin título")
            
            pub_date_dict = work_summary.get("publication-date", {})
            year = pub_date_dict.get("year", {}).get("value", "1900") if pub_date_dict else "1900"
            month = pub_date_dict.get("month", {}).get("value", "01") if pub_date_dict and pub_date_dict.get("month") else "01"
            day = pub_date_dict.get("day", {}).get("value", "01") if pub_date_dict and pub_date_dict.get("day") else "01"
            
            date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
            type_pub = work_summary.get("type", "Journal Article").replace("-", " ").title()
            
            url_pub = ""
            external_ids = work_summary.get("external-ids", {}).get("external-id", [])
            for ext_id in external_ids:
                if ext_id.get("external-id-type") == "doi":
                    url_pub = f"https://doi.org/{ext_id.get('external-id-value')}"
                    break

            pub_entry = {
                "title": title,
                "date": date_str,
                "categories": [type_pub, year],
                "description": f"Publicado en: {work_summary.get('journal-title', {}).get('value', 'N/A') if work_summary.get('journal-title') else 'N/A'}"
            }
            if url_pub:
                pub_entry["path"] = url_pub

            publications.append(pub_entry)

        with open("publications.yml", "w", encoding="utf-8") as f:
            yaml.dump(publications, f, allow_unicode=True, default_flow_style=False)
        print(" -> [Hook] publicaciones.yml actualizado con éxito desde ORCID.")
    else:
        print(" -> [Hook] Aviso: No se pudo actualizar ORCID (Código de estado no 200). Usando copia local existente.")
except Exception as e:
    print(f" -> [Hook] Aviso: Error al conectar con ORCID ({e}). Usando copia local existente.")
