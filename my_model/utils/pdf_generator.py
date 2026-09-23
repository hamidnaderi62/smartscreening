"""Backward-compatible import for the current PDF report service."""

from ..services.report_pdf import generate_pdf_report

__all__ = ('generate_pdf_report',)
