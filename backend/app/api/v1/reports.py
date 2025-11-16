"""Verification report API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.models.company import Company
from app.models.user import User
from app.core.auth import get_current_active_user
from app.core.audit import log_audit_event
from app.services.report_generator import ReportGenerator
from app.utils.exporters import ReportExporter
from fastapi import Request
import io

router = APIRouter()


@router.get("/company/{company_id}/report")
async def get_verification_report(
    company_id: UUID,
    verification_result_id: Optional[UUID] = Query(None, description="Optional specific verification result ID"),
    format: str = Query("json", description="Export format: json, csv, pdf, html"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Generate and return verification report"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Log audit event
    log_audit_event(
        db=db,
        user=current_user,
        action="GENERATE_REPORT",
        resource_type="company",
        resource_id=company.id,
        details={"legal_name": company.legal_name, "format": format},
        request=request
    )
    
    # Generate report
    report_generator = ReportGenerator(db)
    try:
        report_data = report_generator.generate_report(company_id, verification_result_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # Export in requested format
    exporter = ReportExporter()
    
    if format.lower() == "json":
        return JSONResponse(
            content=report_data,
            headers={
                "Content-Disposition": f'attachment; filename="report_{company_id}_{report_data["report_metadata"]["report_id"]}.json"'
            }
        )
    
    elif format.lower() == "csv":
        csv_content = exporter.export_csv(report_data)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="report_{company_id}_{report_data["report_metadata"]["report_id"]}.csv"'
            }
        )
    
    elif format.lower() == "pdf":
        pdf_content = exporter.export_pdf(report_data)
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="report_{company_id}_{report_data["report_metadata"]["report_id"]}.pdf"'
            }
        )
    
    elif format.lower() in ["html", "print"]:
        html_content = exporter.export_print_friendly(report_data)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f'inline; filename="report_{company_id}_{report_data["report_metadata"]["report_id"]}.html"'
            }
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Supported formats: json, csv, pdf, html"
        )


@router.get("/company/{company_id}/report/json")
async def get_verification_report_json(
    company_id: UUID,
    verification_result_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get verification report as JSON (convenience endpoint)"""
    return await get_verification_report(
        company_id=company_id,
        verification_result_id=verification_result_id,
        format="json",
        db=db,
        current_user=current_user
    )


@router.get("/company/{company_id}/report/csv")
async def get_verification_report_csv(
    company_id: UUID,
    verification_result_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get verification report as CSV (convenience endpoint)"""
    return await get_verification_report(
        company_id=company_id,
        verification_result_id=verification_result_id,
        format="csv",
        db=db,
        current_user=current_user
    )


@router.get("/company/{company_id}/report/pdf")
async def get_verification_report_pdf(
    company_id: UUID,
    verification_result_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get verification report as PDF (convenience endpoint)"""
    return await get_verification_report(
        company_id=company_id,
        verification_result_id=verification_result_id,
        format="pdf",
        db=db,
        current_user=current_user
    )

