from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    year = datetime.today()
    return {"year": year.year}
