# User Guide
## Enterprise Company Verification Intelligence (ECVI)

**Version:** 1.0  
**Date:** 2025  
**Audience:** Compliance Officers, IT Security Teams, Business Analysts

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Roles and Permissions](#user-roles-and-permissions)
3. [Company Management](#company-management)
4. [Verification Process](#verification-process)
5. [Reports and Analytics](#reports-and-analytics)
6. [Data Management](#data-management)
7. [Security and Compliance](#security-and-compliance)
8. [Troubleshooting](#troubleshooting)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [FAQ](#faq)

---

## Getting Started

### Logging In

1. Navigate to the ECVI application URL
2. Enter your email address and password
3. Click "Sign In"
4. You will be redirected to the Dashboard upon successful login

### First-Time Login

If this is your first time logging in:
- You will see the Dashboard with an overview of the system
- Review the welcome message and key metrics
- Familiarize yourself with the navigation menu

### Dashboard Overview

The Dashboard provides:
- **Total Companies:** Number of companies in the system
- **Pending Verifications:** Companies awaiting verification
- **High-Risk Companies:** Companies flagged as high risk
- **Recent Activity:** Latest verification results

---

## User Roles and Permissions

### Compliance Officer (Operator)

**Permissions:**
- Create and manage companies
- View all verification reports
- Mark companies as reviewed
- Propose data corrections
- Export reports
- View audit logs

**Restrictions:**
- Cannot approve data corrections (admin only)
- Cannot access security audit features

### IT Security Team (Admin)

**Permissions:**
- All Compliance Officer permissions
- Approve/reject data corrections
- Access security audit features
- View failed login attempts
- Manage user accounts (if applicable)
- Access all system settings

### Business Analyst (Viewer)

**Permissions:**
- View companies and reports
- Export reports
- View historical data and trends
- Generate shareable report links

**Restrictions:**
- Cannot create or modify companies
- Cannot mark reviews
- Cannot propose corrections

---

## Company Management

### Creating a Company

1. Click "Create Company" button (top right of Company List)
2. Fill in the required fields:
   - **Legal Name:** Official company name (required)
   - **Registration Number:** Company registration number (optional)
   - **Jurisdiction:** Country or state of registration (optional)
   - **Domain:** Company website domain (optional)
3. Click "Create Company"
4. The company will be created and verification will start automatically

**Note:** Verification typically takes 1-2 hours. You can monitor the status in real-time.

### Viewing Company List

The Company List shows all companies with:
- Company name
- Risk score and category
- Verification status
- Review status
- Last updated date

**Features:**
- **Search:** Type in the search box to find companies by name
- **Filters:** Use filters to narrow down results:
  - Risk Category (Low, Medium, High)
  - Verification Status (Pending, In Progress, Completed, Failed)
  - Review Status (Reviewed, Pending, Flagged)
- **Pagination:** Navigate through pages of results

### Viewing Company Details

1. Click on a company name from the list
2. View comprehensive company information:
   - Company registration details
   - Contact information
   - Verification results
   - Risk score breakdown
   - Verification history
   - Review history
   - Data corrections (if any)

---

## Verification Process

### Automatic Verification

When a company is created, verification starts automatically. The process includes:

1. **Data Collection:** AI agents gather company information from multiple sources
2. **Verification:** Data is verified and cross-referenced
3. **Risk Assessment:** Risk score is calculated
4. **Report Generation:** Comprehensive report is generated

### Monitoring Verification Status

**Status Indicators:**
- 🟡 **Pending:** Verification not yet started
- 🔵 **In Progress:** Verification in progress
- 🟢 **Completed:** Verification completed successfully
- 🔴 **Failed:** Verification failed (check error details)

**Real-Time Updates:**
- Status updates automatically
- Notifications appear when verification completes
- You can refresh the page to see latest status

### Re-triggering Verification

If you need to re-verify a company:

1. Navigate to company details
2. Click "Re-trigger Analysis" button
3. Confirm the action
4. New verification will start
5. Previous results are preserved for comparison

---

## Reports and Analytics

### Viewing Verification Reports

1. Navigate to company details
2. Scroll to "Verification Report" section
3. Review all sections:
   - Company Registration Data
   - Contact Information
   - HQ Address
   - DNS Verification Results
   - Risk Score Breakdown
   - Data Source Attribution
   - Confidence Scores
   - Discrepancies (if any)

### Exporting Reports

Reports can be exported in multiple formats:

1. Click "Export Report" button
2. Select format:
   - **JSON:** For data analysis
   - **CSV:** For spreadsheet analysis
   - **PDF:** For documentation
   - **HTML:** For printing
3. Report will download automatically

### Sharing Reports

1. Click "Share Report" button
2. Generate shareable link
3. Copy the link
4. Share with stakeholders (link works without login)
5. Link expires after set period (default: 30 days)

### Risk Score Analysis

**Understanding Risk Scores:**
- **0-30 (Low Risk):** ✅ Green indicator - Low risk, likely legitimate
- **31-70 (Medium Risk):** ⚠️ Yellow indicator - Moderate risk, review recommended
- **71-100 (High Risk):** 🔴 Red indicator - High risk, immediate review required

**Risk Score Breakdown:**
- DNS Verification Risk
- Registration Consistency
- Contact Validation
- Domain Authenticity
- Cross-Source Validation

**Historical Trends:**
- View risk score trends over time
- Compare multiple verifications
- Identify risk patterns

---

## Data Management

### Manual Review Marking

Mark companies as reviewed to track your review process:

1. Navigate to company details
2. Click "Mark as Reviewed" button
3. Select review status:
   - **Approved:** Company verified and approved
   - **Flagged:** Requires additional review
   - **Rejected:** Company rejected
4. Add review notes (optional)
5. Submit review

**Review History:**
- All reviews are tracked
- Review history is visible in company details
- Reviews can be edited (latest review)

### Data Correction

If you find incorrect data in a verification report:

1. Navigate to company details
2. Click "Correct Data" button next to the field
3. Enter corrected value
4. Provide reason for correction
5. Submit correction proposal
6. Admin will review and approve/reject

**Correction Workflow:**
- Corrections are tracked with version history
- Previous values are preserved
- After approval, verification can be re-run with corrected data

### Verification History

View complete verification history for a company:

1. Navigate to company details
2. Scroll to "Verification History" section
3. View all past verifications:
   - Date and time
   - Risk score
   - Status
   - Key findings
4. Compare verifications side-by-side
5. View trend charts

---

## Security and Compliance

### Audit Logs

All user actions are logged for compliance:

- Company creation and updates
- Review markings
- Data corrections
- Report exports
- Login/logout events

**Accessing Audit Logs:**
- Navigate to Audit Logs (Admin only)
- Filter by user, action, date range
- Export audit logs for compliance reporting

### Security Features

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Session Management:**
- Sessions timeout after inactivity
- You will be logged out automatically
- Re-login required after timeout

### GDPR Compliance

**Data Access:**
- You can view all data associated with your account
- Data can be exported in standard formats
- Data retention follows GDPR guidelines

**Data Correction:**
- Incorrect data can be corrected
- Correction history is maintained
- Data accuracy is ensured

---

## Troubleshooting

### Common Issues

**Issue: Verification taking too long**
- **Solution:** Verifications typically take 1-2 hours. If longer, check system status or contact support.

**Issue: Cannot see company in list**
- **Solution:** Check filters - they may be hiding the company. Clear filters and search again.

**Issue: Export not working**
- **Solution:** Check browser popup blocker. Allow popups for the site and try again.

**Issue: Report data seems incorrect**
- **Solution:** Check verification date. Data may be outdated. Re-trigger verification if needed.

**Issue: Cannot log in**
- **Solution:** Verify credentials. Check if account is active. Contact admin if issues persist.

### Getting Help

- **In-App Help:** Click help icon (?) for context-sensitive help
- **Documentation:** Access full documentation from help menu
- **Support:** Contact support team for technical issues
- **Training:** Request training session for your team

---

## Keyboard Shortcuts

- **Ctrl/Cmd + K:** Quick search
- **Ctrl/Cmd + /** : Show keyboard shortcuts
- **Esc:** Close modal/dialog
- **Tab:** Navigate between fields
- **Enter:** Submit form
- **Arrow Keys:** Navigate lists

---

## FAQ

### General Questions

**Q: How long does verification take?**
A: Typically 1-2 hours, but can vary based on data complexity and system load.

**Q: Can I cancel a verification?**
A: No, but you can start a new verification which will create a new result.

**Q: How accurate is the risk score?**
A: Risk scores are based on comprehensive data analysis and cross-referencing. They should be used as a guide, not absolute truth.

**Q: Can I edit verification results?**
A: No, but you can propose data corrections which, when approved, will trigger a new verification.

### Technical Questions

**Q: What browsers are supported?**
A: Modern browsers (Chrome, Firefox, Safari, Edge) - latest 2 versions.

**Q: Is the system mobile-friendly?**
A: Yes, the system is responsive and works on mobile devices, though desktop is recommended for full functionality.

**Q: How often is data updated?**
A: Verification data is updated when a new verification is run. Historical data is preserved.

**Q: Can I integrate with other systems?**
A: API documentation is available for integration. Contact support for API access.

### Security Questions

**Q: Is my data secure?**
A: Yes, the system uses industry-standard security measures including encryption, secure authentication, and audit logging.

**Q: Who can see my data?**
A: Data access is controlled by role-based permissions. Only authorized users can access data.

**Q: How long is data retained?**
A: Data retention follows GDPR guidelines. Contact admin for specific retention policies.

---

## Best Practices

### For Compliance Officers

1. **Regular Reviews:** Review high-risk companies immediately
2. **Documentation:** Use review notes to document decisions
3. **Data Accuracy:** Propose corrections when you find errors
4. **Reports:** Export reports for compliance documentation
5. **Monitoring:** Check pending verifications regularly

### For IT Security Teams

1. **High-Risk Focus:** Prioritize high-risk company reviews
2. **Audit Logs:** Regularly review audit logs for suspicious activity
3. **Security Monitoring:** Use security audit features proactively
4. **Access Control:** Verify role-based permissions are correct
5. **Incident Response:** Use reports for security incident documentation

### For Business Analysts

1. **Trend Analysis:** Use historical data to identify patterns
2. **Risk Assessment:** Use risk scores to inform business decisions
3. **Reporting:** Generate reports for stakeholders
4. **Data Export:** Export data for further analysis
5. **Sharing:** Use shareable links to distribute reports

---

## Glossary

- **Verification:** Process of collecting and validating company information
- **Risk Score:** Numeric score (0-100) indicating company risk level
- **Verification Status:** Current state of verification (Pending, In Progress, Completed, Failed)
- **Review Status:** Manual review status (Approved, Flagged, Rejected, Pending)
- **Data Correction:** Proposal to correct incorrect verification data
- **Audit Log:** Record of all user actions for compliance
- **Shareable Link:** Token-based link to access reports without login

---

**Document Version:** 1.0  
**Last Updated:** 2025  
**For Support:** Contact your system administrator or support team

