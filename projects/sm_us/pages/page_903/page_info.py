# common/pages/page_903/page_info.py
"""
Page information for page 903 (Document Preview/Edit)
"""

def get_page_903_url(domain, doc_id=1, phase="edit", preview_doc=1):
    """
    Returns the URL for page 903 for the specified domain and document ID
    
    Args:
        domain: Full domain name (e.g., "stage4.office.sovasystem.com")
        doc_id: Document ID to edit (default: 1)
        phase: Document phase (default: "edit")
        preview_doc: Preview document flag (default: 1)
        
    Returns:
        str: URL for page 903
    """
    return f"https://{domain}/sage/index.cfm?page_id=903&preview_doc={preview_doc}&phase={phase}&id={doc_id}"

def get_login_url(domain):
    """
    Returns the login URL for the specified domain
    
    Args:
        domain: Full domain name (e.g., "stage4.office.sovasystem.com")
        
    Returns:
        str: Login URL for the domain
    """
    return f"https://{domain}/sage/?logout"