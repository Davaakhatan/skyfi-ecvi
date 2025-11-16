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
from app.services.report_sharing import ReportSharingService, SharedReport
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
    
    # Get report ID safely
    report_id = report_data.get("report_metadata", {}).get("report_id", str(company_id))
    
    if format.lower() == "json":
        return JSONResponse(
            content=report_data,
            headers={
                "Content-Disposition": f'attachment; filename="report_{company_id}_{report_id}.json"'
            }
        )
    
    elif format.lower() == "csv":
        csv_content = exporter.export_csv(report_data)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="report_{company_id}_{report_id}.csv"'
            }
        )
    
    elif format.lower() == "pdf":
        pdf_content = exporter.export_pdf(report_data)
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="report_{company_id}_{report_id}.pdf"'
            }
        )
    
    elif format.lower() in ["html", "print"]:
        html_content = exporter.export_print_friendly(report_data)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f'inline; filename="report_{company_id}_{report_id}.html"'
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


@router.post("/company/{company_id}/report/share")
async def create_shareable_link(
    company_id: UUID,
    verification_result_id: Optional[UUID] = Query(None, description="Optional specific verification result ID"),
    expires_in_days: Optional[int] = Query(30, ge=1, le=365, description="Number of days until link expires"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Create a shareable link for a verification report"""
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
        action="CREATE_SHAREABLE_LINK",
        resource_type="company",
        resource_id=company.id,
        details={"legal_name": company.legal_name, "expires_in_days": expires_in_days},
        request=request
    )
    
    try:
        share_info = ReportSharingService.create_shareable_link(
            db=db,
            company_id=company_id,
            verification_result_id=verification_result_id,
            created_by=current_user.id,
            expires_in_days=expires_in_days
        )
        
        return {
            "success": True,
            "share_token": share_info["share_token"],
            "share_url": share_info["share_url"],
            "expires_at": share_info["expires_at"],
            "created_at": share_info["created_at"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/shared/{share_token}")
async def get_shared_report(
    share_token: str,
    format: str = Query("json", description="Export format: json, csv, pdf, html"),
    db: Session = Depends(get_db)
):
    """Get verification report via shareable link (no authentication required)"""
    # Get shared report
    shared_report = ReportSharingService.get_shared_report(db, share_token)
    
    if not shared_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shareable link not found, expired, or revoked"
        )
    
    # Generate report
    report_generator = ReportGenerator(db)
    try:
        report_data = report_generator.generate_report(
            shared_report.company_id,
            shared_report.verification_result_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # Export in requested format
    exporter = ReportExporter()
    
    if format.lower() == "json":
        return JSONResponse(content=report_data)
    elif format.lower() == "csv":
        csv_content = exporter.export_csv(report_data)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="report_{shared_report.company_id}.csv"'
            }
        )
    elif format.lower() == "pdf":
        pdf_content = exporter.export_pdf(report_data)
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="report_{shared_report.company_id}.pdf"'
            }
        )
    elif format.lower() in ["html", "print"]:
        html_content = exporter.export_print_friendly(report_data)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f'inline; filename="report_{shared_report.company_id}.html"'
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Supported formats: json, csv, pdf, html"
        )


@router.get("/company/{company_id}/report/shares")
async def list_shareable_links(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all shareable links for a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    links = ReportSharingService.list_shared_links(
        db=db,
        company_id=company_id,
        user_id=current_user.id
    )
    
    return {
        "company_id": str(company_id),
        "total_links": len(links),
        "links": links
    }


@router.delete("/company/{company_id}/report/share/{share_token}")
async def revoke_shareable_link(
    company_id: UUID,
    share_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Revoke a shareable link"""
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
        action="REVOKE_SHAREABLE_LINK",
        resource_type="company",
        resource_id=company.id,
        details={"legal_name": company.legal_name, "share_token": share_token},
        request=request
    )
    
    success = ReportSharingService.revoke_shareable_link(
        db=db,
        share_token=share_token,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shareable link not found"
        )
    
    return {
        "success": True,
        "message": "Shareable link revoked successfully"
    }

