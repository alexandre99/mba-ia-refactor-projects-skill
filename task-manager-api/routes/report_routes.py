from flask import Blueprint

from controllers.report_controller import summary as summary_controller
from controllers.report_controller import user_report as user_report_controller
from controllers.response import execute

report_bp = Blueprint("reports", __name__)


@report_bp.route("/reports/summary", methods=["GET"])
def summary_report():
    return execute(summary_controller)


@report_bp.route("/reports/user/<int:user_id>", methods=["GET"])
def user_report(user_id):
    return execute(lambda: user_report_controller(user_id))
