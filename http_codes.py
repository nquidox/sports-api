from fastapi import HTTPException, status


c403 = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Resource is available but not accessible because of permissions',
        headers={})
