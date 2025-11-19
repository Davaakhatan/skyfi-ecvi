# Operator Troubleshooting Guide
## Enterprise Company Verification Intelligence (ECVI)

**Version:** 1.0  
**Date:** 2025

---

## Table of Contents

1. [Login Issues](#login-issues)
2. [Company Management Issues](#company-management-issues)
3. [Verification Issues](#verification-issues)
4. [Report Issues](#report-issues)
5. [Data Correction Issues](#data-correction-issues)
6. [Performance Issues](#performance-issues)
7. [Browser Issues](#browser-issues)

---

## Login Issues

### Cannot Log In

**Symptoms:**
- "Invalid email or password" error
- Page doesn't respond
- Redirects back to login

**Solutions:**

1. **Verify Credentials**
   - Check email spelling
   - Verify password (case-sensitive)
   - Try password reset if available

2. **Clear Browser Cache**
   ```
   Chrome: Settings → Privacy → Clear browsing data
   Firefox: Settings → Privacy → Clear Data
   Safari: Develop → Empty Caches
   ```

3. **Check Browser Console**
   - Press F12 to open developer tools
   - Check Console tab for errors
   - Check Network tab for failed requests

4. **Try Different Browser**
   - Use Chrome, Firefox, or Safari
   - Disable browser extensions
   - Try incognito/private mode

5. **Contact Support**
   - If issue persists, contact IT support
   - Provide error messages and browser details

---

### Session Expired

**Symptoms:**
- "Session expired" message
- Redirected to login page
- Work in progress lost

**Solutions:**

1. **Log Back In**
   - Simply log in again
   - Session timeout is 30 minutes of inactivity

2. **Prevent Future Issues**
   - Keep browser tab active
   - Don't leave page idle for > 30 minutes
   - Save work frequently

3. **Recover Lost Work**
   - Check if data was saved
   - Re-enter information if needed
   - Use browser back button if available

---

## Company Management Issues

### Cannot Create Company

**Symptoms:**
- Form won't submit
- Error message appears
- Company not appearing in list

**Solutions:**

1. **Check Required Fields**
   - Legal Name is required
   - Ensure field is not empty
   - Remove special characters if causing issues

2. **Validate Input**
   - Legal Name: 2-200 characters
   - Registration Number: Alphanumeric only
   - Domain: Valid domain format (e.g., example.com)

3. **Check Network**
   - Verify internet connection
   - Check if API is accessible
   - Try refreshing page

4. **Clear Form and Retry**
   - Clear all fields
   - Re-enter information
   - Submit again

5. **Check Browser Console**
   - Look for JavaScript errors
   - Check Network tab for failed requests
   - Review error messages

---

### Company Not Appearing in List

**Symptoms:**
- Created company not visible
- List not updating
- Search not finding company

**Solutions:**

1. **Refresh List**
   - Click refresh button
   - Press F5 to reload page
   - Clear filters if applied

2. **Check Filters**
   - Remove active filters
   - Check search terms
   - Verify sort order

3. **Search for Company**
   - Use search bar
   - Search by legal name
   - Check different pages if paginated

4. **Verify Creation**
   - Check if creation was successful
   - Look for success message
   - Review browser console for errors

---

### Cannot Edit Company

**Symptoms:**
- Edit button not visible
- Changes not saving
- Permission denied error

**Solutions:**

1. **Check Permissions**
   - Verify you have operator role
   - Contact admin if permissions incorrect
   - Check if company is locked

2. **Use Data Correction**
   - Operators cannot directly edit
   - Use "Propose Correction" instead
   - Wait for admin approval

3. **Check Company Status**
   - Some companies may be locked
   - Check if verification is in progress
   - Wait for verification to complete

---

## Verification Issues

### Verification Not Starting

**Symptoms:**
- Status remains "PENDING"
- No progress indicator
- Error message displayed

**Solutions:**

1. **Wait and Refresh**
   - Verification may take a moment to start
   - Wait 1-2 minutes
   - Refresh page to check status

2. **Check Company Data**
   - Verify minimum required data exists
   - Ensure domain is valid (if provided)
   - Check for data format issues

3. **Re-trigger Verification**
   - Click "Re-trigger Analysis"
   - Confirm re-trigger
   - Monitor new verification

4. **Check System Status**
   - Verify backend is running
   - Check for system maintenance
   - Contact support if issue persists

---

### Verification Taking Too Long

**Symptoms:**
- Status "IN_PROGRESS" for > 2 hours
- No completion notification
- System seems stuck

**Solutions:**

1. **Check Expected Duration**
   - Normal: Up to 2 hours
   - Complex companies may take longer
   - Check verification history for patterns

2. **Review Company Complexity**
   - More data sources = longer time
   - International companies may take longer
   - Check if company has many subsidiaries

3. **Re-trigger if Needed**
   - If > 3 hours, consider re-triggering
   - Previous results are preserved
   - New verification will start

4. **Contact Support**
   - Provide company ID
   - Share verification start time
   - Include any error messages

---

### Verification Failed

**Symptoms:**
- Status shows "FAILED"
- Error message displayed
- No results available

**Solutions:**

1. **Review Error Message**
   - Check error details in company detail
   - Look for specific failure reason
   - Note any error codes

2. **Check Company Data**
   - Verify data is complete
   - Check for invalid formats
   - Ensure domain is accessible (if provided)

3. **Try Re-triggering**
   - Click "Re-trigger Analysis"
   - System will retry verification
   - Previous attempt is logged

4. **Manual Review**
   - If automated verification fails
   - Perform manual review
   - Add notes explaining situation

---

## Report Issues

### Report Not Generating

**Symptoms:**
- Export button not working
- Report generation fails
- Download doesn't start

**Solutions:**

1. **Verify Verification Complete**
   - Report requires completed verification
   - Check verification status
   - Wait for verification if in progress

2. **Try Different Format**
   - Try JSON instead of PDF
   - Use CSV for smaller reports
   - HTML format is usually fastest

3. **Wait for Generation**
   - Large reports take time
   - Wait up to 30 seconds
   - Don't close browser tab

4. **Check Browser Settings**
   - Ensure downloads are enabled
   - Check download folder permissions
   - Disable pop-up blockers

5. **Clear Browser Cache**
   - Clear cache and cookies
   - Try incognito mode
   - Use different browser

---

### Report Data Incomplete

**Symptoms:**
- Missing sections in report
- Incomplete verification data
- Empty fields

**Solutions:**

1. **Check Verification Status**
   - Ensure verification is "COMPLETED"
   - Check if all components verified
   - Review verification details

2. **Verify Data Availability**
   - Some data may not be available
   - Check data sources section
   - Review confidence scores

3. **Re-generate Report**
   - Try exporting again
   - Use different format
   - Wait a moment and retry

4. **Check Report Version**
   - Reports reflect current data
   - Re-export if data was updated
   - Check report generation time

---

### Shareable Link Not Working

**Symptoms:**
- Link returns error
- Report not accessible
- "Link expired" message

**Solutions:**

1. **Check Link Expiration**
   - Links expire after 30 days (default)
   - Generate new link if expired
   - Check expiration date

2. **Verify Link Format**
   - Ensure full URL is copied
   - Check for truncation
   - Try copying link again

3. **Check Permissions**
   - Shareable links are public
   - No login required
   - Verify link wasn't revoked

4. **Generate New Link**
   - Create new shareable link
   - Update expiration if needed
   - Share new link with stakeholders

---

## Data Correction Issues

### Cannot Propose Correction

**Symptoms:**
- "Correct Data" button not visible
- Correction form won't submit
- Permission error

**Solutions:**

1. **Check Field Availability**
   - Not all fields can be corrected
   - Check if field is editable
   - Verify field has current value

2. **Verify Input**
   - New value must be different
   - Reason is required
   - Check field format requirements

3. **Check Pending Corrections**
   - Only one pending correction per field
   - Check correction history
   - Wait for existing correction to be processed

4. **Contact Admin**
   - If correction is urgent
   - Request admin review
   - Provide correction details

---

### Correction Not Approved

**Symptoms:**
- Correction status "REJECTED"
- No explanation provided
- Correction not applied

**Solutions:**

1. **Review Rejection Reason**
   - Check correction details
   - Read admin notes
   - Understand rejection reason

2. **Verify Correction Data**
   - Ensure new value is correct
   - Check data sources
   - Verify correction reason

3. **Resubmit if Appropriate**
   - Fix issues identified
   - Provide better justification
   - Submit new correction

4. **Contact Admin**
   - Discuss rejection if unclear
   - Provide additional context
   - Request clarification

---

## Performance Issues

### Slow Page Loading

**Symptoms:**
- Pages take long to load
- Spinning loader persists
- Timeout errors

**Solutions:**

1. **Check Internet Connection**
   - Verify connection speed
   - Test other websites
   - Try different network

2. **Clear Browser Cache**
   - Clear cache and cookies
   - Remove old data
   - Restart browser

3. **Reduce Data Load**
   - Use filters to reduce list size
   - Limit search results
   - Close unused tabs

4. **Check System Status**
   - Verify system is operational
   - Check for maintenance notices
   - Contact support if issue persists

---

### Search Not Working

**Symptoms:**
- Search returns no results
- Search is slow
- Results are incorrect

**Solutions:**

1. **Check Search Terms**
   - Verify spelling
   - Try partial matches
   - Use different keywords

2. **Clear Search and Retry**
   - Clear search field
   - Remove filters
   - Try new search term

3. **Check Search Scope**
   - Search covers: name, registration, domain
   - Use exact matches when possible
   - Try broader terms

4. **Refresh and Retry**
   - Refresh page
   - Clear browser cache
   - Try again

---

## Browser Issues

### Browser Compatibility

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**If Using Unsupported Browser:**
- Update to latest version
- Use supported browser
- Contact IT for assistance

---

### JavaScript Errors

**Symptoms:**
- Features not working
- Console shows errors
- Page behaves unexpectedly

**Solutions:**

1. **Enable JavaScript**
   - Check browser settings
   - Ensure JavaScript is enabled
   - Disable blocking extensions

2. **Update Browser**
   - Install latest version
   - Enable auto-updates
   - Restart browser

3. **Disable Extensions**
   - Disable ad blockers
   - Turn off privacy extensions
   - Test in incognito mode

---

## Getting Help

### Self-Service Resources

1. **Documentation**
   - User Guide
   - Quick Reference
   - API Documentation

2. **System Health**
   - Check `/health` endpoint
   - Review system status page
   - Check maintenance schedule

3. **Common Solutions**
   - Review this guide
   - Check FAQ section
   - Search knowledge base

### Contact Support

**When to Contact:**
- Issue not resolved by troubleshooting
- System error or bug
- Feature request
- Training questions

**Information to Provide:**
- Description of issue
- Steps to reproduce
- Error messages
- Browser and OS details
- Screenshots if helpful

**Support Channels:**
- Email: support@example.com
- Phone: +1-XXX-XXX-XXXX
- Ticket System: (if available)

---

**Last Updated:** 2025

