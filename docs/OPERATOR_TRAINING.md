# Operator Training Guide
## Enterprise Company Verification Intelligence (ECVI)

**Version:** 1.0  
**Date:** 2025  
**Audience:** Compliance Officers (Operators)

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Getting Started](#getting-started)
4. [Core Workflows](#core-workflows)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Common Scenarios](#common-scenarios)
8. [Troubleshooting](#troubleshooting)
9. [Assessment](#assessment)

---

## Introduction

### Welcome to ECVI

The Enterprise Company Verification Intelligence (ECVI) system automates company verification during Enterprise account registration. As a Compliance Officer (Operator), you'll use this system to:

- Register and verify companies
- Review verification results
- Manage data corrections
- Generate compliance reports

### Training Objectives

By the end of this training, you will be able to:
- Navigate the ECVI interface confidently
- Create and manage company records
- Interpret verification results and risk scores
- Perform manual reviews and data corrections
- Generate and export verification reports
- Troubleshoot common issues

### Training Duration

- **Self-paced:** 2-3 hours
- **Instructor-led:** 1.5 hours
- **Hands-on practice:** 30 minutes

---

## System Overview

### What is ECVI?

ECVI is an AI-powered system that:
1. **Collects** company data from multiple sources
2. **Verifies** information across databases
3. **Calculates** risk scores (0-100)
4. **Generates** comprehensive verification reports

### Key Components

- **Company List** - View and manage all companies
- **Company Detail** - View verification results and reports
- **Dashboard** - System overview and metrics
- **Reports** - Export verification data

### Your Role as Operator

**Responsibilities:**
- Create company records
- Review verification results
- Mark companies as reviewed
- Propose data corrections
- Export reports for compliance

**Permissions:**
- ✅ Create and view companies
- ✅ View all verification reports
- ✅ Mark companies as reviewed
- ✅ Propose data corrections
- ✅ Export reports
- ❌ Approve data corrections (Admin only)
- ❌ Access security features (Admin only)

---

## Getting Started

### First Login

1. Navigate to the ECVI application URL
2. Enter your email and password
3. Click "Sign In"
4. You'll see the Dashboard

### Dashboard Overview

The Dashboard shows:
- **Total Companies** - All companies in the system
- **Pending Verifications** - Companies awaiting verification
- **High-Risk Companies** - Companies with risk score > 70
- **Recent Activity** - Latest verification results

### Navigation

- **Dashboard** - System overview
- **Companies** - Company list and management
- **User Menu** - Profile and logout

---

## Core Workflows

### Workflow 1: Register and Verify a Company

**Objective:** Register a new company and initiate verification

**Steps:**

1. **Navigate to Companies**
   - Click "Companies" in the navigation menu
   - Click "Create Company" button (top right)

2. **Enter Company Information**
   - **Legal Name** (required): Official company name
   - **Registration Number** (optional): Company registration number
   - **Jurisdiction** (optional): Country/state of registration
   - **Domain** (optional): Company website domain

3. **Submit and Verify**
   - Click "Create" button
   - System automatically starts verification
   - You'll be redirected to company detail page

4. **Monitor Verification**
   - Status shows "IN_PROGRESS" initially
   - Wait for completion (typically < 2 hours)
   - Status changes to "COMPLETED" when done

**Expected Result:**
- Company created successfully
- Verification process started
- Risk score calculated
- Report generated

---

### Workflow 2: Review Verification Results

**Objective:** Review and understand verification results

**Steps:**

1. **Open Company Detail**
   - Click on company name from the list
   - View verification status and risk score

2. **Review Risk Score**
   - **Low (0-30):** Low risk, minimal concerns
   - **Medium (31-70):** Moderate risk, review recommended
   - **High (71-100):** High risk, requires investigation

3. **Check Verification Details**
   - **DNS Verification:** Domain authenticity
   - **Registration Verification:** Registration data consistency
   - **Contact Verification:** Email and phone validation
   - **Address Verification:** HQ address completeness

4. **Review Discrepancies**
   - Check for data inconsistencies
   - Review confidence scores
   - Examine data sources

**Key Indicators:**
- 🟢 **Green:** Verified match
- 🟡 **Yellow:** Partial match/warning
- 🔴 **Red:** Discrepancy detected

---

### Workflow 3: Mark Company as Reviewed

**Objective:** Document your review of a company

**Steps:**

1. **Open Company Detail**
   - Navigate to the company you've reviewed

2. **Click "Mark as Reviewed"**
   - Button appears in the company detail page
   - Opens review modal

3. **Add Review Information**
   - **Status:** Select Reviewed, Flagged, or Approved
   - **Notes:** Add any relevant notes
   - **Tags:** Add tags for categorization (optional)

4. **Submit Review**
   - Click "Save Review"
   - Review status updates immediately

**Best Practice:**
- Always add notes explaining your decision
- Use consistent tags for categorization
- Review high-risk companies first

---

### Workflow 4: Propose Data Correction

**Objective:** Correct inaccurate company data

**Steps:**

1. **Identify Incorrect Data**
   - View company detail page
   - Identify field with incorrect data

2. **Click "Correct Data"**
   - Button next to the field
   - Opens correction modal

3. **Enter Correction**
   - **Field Name:** Select field to correct
   - **Current Value:** Shows existing value
   - **New Value:** Enter corrected value
   - **Reason:** Explain why correction is needed

4. **Submit Correction**
   - Click "Propose Correction"
   - Status: "PENDING" (awaiting admin approval)

5. **Track Status**
   - View correction history
   - Wait for admin approval/rejection
   - Receive notification when processed

**Note:** Corrections require admin approval before being applied.

---

### Workflow 5: Export Verification Report

**Objective:** Generate and export verification report

**Steps:**

1. **Open Company Detail**
   - Navigate to company with completed verification

2. **Click "Export Report"**
   - Button in the company detail page
   - Select export format:
     - **JSON** - Machine-readable format
     - **CSV** - Spreadsheet format
     - **PDF** - Document format
     - **HTML** - Print-friendly format

3. **Download Report**
   - Report generates (typically < 30 seconds)
   - File downloads automatically

4. **Share Report (Optional)**
   - Click "Share Report"
   - Generate shareable link
   - Copy link to share with stakeholders

**Report Contents:**
- Company information
- Risk assessment
- Verification details
- Data sources
- Confidence scores
- Discrepancies (if any)

---

## Advanced Features

### Re-trigger Verification

**When to Use:**
- Company information has changed
- Previous verification failed
- Need updated risk assessment

**Steps:**
1. Open company detail page
2. Click "Re-trigger Analysis"
3. Confirm re-trigger
4. Monitor new verification process
5. Compare old vs. new results

### View Verification History

**Access:**
- Company detail page
- "Verification History" section
- Shows all past verifications

**Information Displayed:**
- Risk score trends
- Verification date/time
- Status changes
- Historical comparisons

### Filter and Search Companies

**Search:**
- Use search bar in company list
- Search by company name, registration number, or domain

**Filters:**
- **Risk Level:** Low, Medium, High
- **Review Status:** Reviewed, Pending, Flagged
- **Verification Status:** Completed, In Progress, Failed

**Sort:**
- By creation date
- By risk score
- By company name

---

## Best Practices

### 1. Company Registration

✅ **Do:**
- Enter complete information when available
- Use official company names
- Include registration numbers for accuracy
- Verify domain names before entering

❌ **Don't:**
- Use abbreviations unless official
- Enter placeholder data
- Skip optional fields if data is available

### 2. Review Process

✅ **Do:**
- Review high-risk companies first
- Add detailed notes explaining decisions
- Use consistent tags for categorization
- Review within 24 hours of verification

❌ **Don't:**
- Mark as reviewed without examining results
- Skip reviewing discrepancies
- Ignore confidence scores

### 3. Data Corrections

✅ **Do:**
- Provide clear reasons for corrections
- Include source of correct information
- Verify correction before submitting
- Follow up on pending corrections

❌ **Don't:**
- Submit corrections without justification
- Correct data based on assumptions
- Submit duplicate corrections

### 4. Report Management

✅ **Do:**
- Export reports in appropriate format
- Store reports securely
- Share reports only with authorized personnel
- Use shareable links for external sharing

❌ **Don't:**
- Share reports publicly
- Store reports in unsecured locations
- Modify exported reports

---

## Common Scenarios

### Scenario 1: High-Risk Company Registration

**Situation:** New company registered with risk score of 85 (High)

**Actions:**
1. Review verification details immediately
2. Check all discrepancies
3. Examine data sources
4. Review contact information
5. Mark as "Flagged" with detailed notes
6. Export report for security team
7. Escalate to admin if needed

### Scenario 2: Verification Timeout

**Situation:** Verification has been "IN_PROGRESS" for > 2 hours

**Actions:**
1. Check system status (health endpoint)
2. Review company detail for error messages
3. Try re-triggering verification
4. Contact support if issue persists
5. Document the issue

### Scenario 3: Data Discrepancy Found

**Situation:** System detects discrepancy in company name

**Actions:**
1. Review discrepancy details
2. Check data sources
3. Verify correct information
4. Propose data correction if needed
5. Add notes explaining the discrepancy
6. Mark review status appropriately

### Scenario 4: Multiple Companies with Same Name

**Situation:** Need to verify which company is correct

**Actions:**
1. Use search to find all companies with similar names
2. Compare registration numbers
3. Check jurisdictions
4. Review verification results for each
5. Use domain information to distinguish
6. Add notes to clarify differences

---

## Troubleshooting

### Issue: Cannot Create Company

**Possible Causes:**
- Missing required field (Legal Name)
- Network connectivity issues
- Session expired

**Solutions:**
1. Verify all required fields are filled
2. Check internet connection
3. Refresh page and try again
4. Log out and log back in
5. Contact support if issue persists

### Issue: Verification Not Starting

**Possible Causes:**
- System overload
- Missing company information
- Service unavailable

**Solutions:**
1. Wait a few minutes and refresh
2. Verify company has minimum required data
3. Check system status
4. Try re-triggering verification
5. Contact support

### Issue: Report Not Generating

**Possible Causes:**
- Verification not completed
- Large report taking time
- System error

**Solutions:**
1. Verify verification status is "COMPLETED"
2. Wait for report generation (up to 30 seconds)
3. Try different export format
4. Refresh page and try again
5. Contact support if issue persists

### Issue: Cannot See Company Data

**Possible Causes:**
- Insufficient permissions
- Company doesn't exist
- Browser cache issues

**Solutions:**
1. Verify you're logged in
2. Check company ID is correct
3. Clear browser cache
4. Try different browser
5. Contact admin to verify permissions

---

## Assessment

### Knowledge Check

1. **What is the risk score range?**
   - Answer: 0-100 (Low: 0-30, Medium: 31-70, High: 71-100)

2. **What happens when you create a company?**
   - Answer: Verification process starts automatically

3. **Who can approve data corrections?**
   - Answer: Admin users only

4. **What export formats are available?**
   - Answer: JSON, CSV, PDF, HTML

5. **How long does verification typically take?**
   - Answer: Up to 2 hours

### Practical Exercise

**Exercise:** Register and review a test company

1. Create a company with the following:
   - Legal Name: "Training Test Company Inc"
   - Registration Number: "TRAIN123"
   - Jurisdiction: "US"
   - Domain: "traintest.com"

2. Wait for verification to complete

3. Review the verification results:
   - Check risk score
   - Review verification details
   - Examine any discrepancies

4. Mark the company as reviewed with notes

5. Export the report as PDF

6. Propose a data correction (if needed)

### Completion Criteria

✅ Can navigate the system confidently  
✅ Can create and manage companies  
✅ Can interpret verification results  
✅ Can perform reviews and corrections  
✅ Can export reports  
✅ Can troubleshoot common issues  

---

## Additional Resources

- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Runbooks:** [RUNBOOKS.md](RUNBOOKS.md)
- **Support:** support@example.com

---

## Training Feedback

After completing this training, please provide feedback:
- What was most helpful?
- What needs clarification?
- Any suggestions for improvement?

**Thank you for completing the ECVI Operator Training!**

---

**Last Updated:** 2025

