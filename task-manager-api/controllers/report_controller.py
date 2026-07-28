from services.report_service import ReportService

service = ReportService()


def summary():
    return service.summary()


def user_report(user_id):
    return service.user_report(user_id)
