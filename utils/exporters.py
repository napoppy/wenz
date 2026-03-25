import os
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from typing import List
from models.data_models import Account
import config


class ExportService:
    @staticmethod
    def export_to_excel(accounts: List[Account], keyword: str, output_dir: str = config.DATA_DIR) -> str:
        if not accounts:
            return ""

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{keyword}_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)

        data = [acc.to_dict() for acc in accounts]
        df = pd.DataFrame(data)

        df.columns = config.EXCEL_COLUMNS

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='账号分析', index=False)

            workbook = writer.book
            worksheet = writer.sheets['账号分析']

            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)

            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')

            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        return filepath

    @staticmethod
    def export_to_csv(accounts: List[Account], keyword: str, output_dir: str = config.DATA_DIR) -> str:
        if not accounts:
            return ""

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{keyword}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        data = [acc.to_dict() for acc in accounts]
        df = pd.DataFrame(data)
        df.columns = config.EXCEL_COLUMNS

        df.to_csv(filepath, index=False, encoding='utf-8-sig')

        return filepath

    @staticmethod
    def get_articles_dataframe(accounts: List[Account]) -> pd.DataFrame:
        all_articles = []
        for account in accounts:
            for article in account.articles:
                all_articles.append(article.to_dict())

        if not all_articles:
            return pd.DataFrame()

        df = pd.DataFrame(all_articles)
        return df


def create_exporter() -> ExportService:
    return ExportService()
