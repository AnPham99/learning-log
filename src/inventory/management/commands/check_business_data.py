import json

from django.core.management.base import BaseCommand, CommandError

from inventory.checks import check_business_data


class Command(BaseCommand):
    help = "Đối chiếu Stock, Movement và chứng từ; chỉ đọc."

    def handle(self, *args, **options):
        result = check_business_data()
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["ok"]:
            raise CommandError("Dữ liệu không khớp. Kiểm tra danh sách lỗi trước khi demo.")
