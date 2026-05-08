# Detailed Changes - Line by Line

## File 1: app/dependencies.py

### Added Imports (Line 2)
```python
from slowapi import Limiter
```

### Added Function (Lines 77-79)
```python
def get_limiter() -> Limiter:
    from app.main import app
    return app.state.limiter
```

---

## File 2: app/api/routes/videos.py

### Added Imports (Lines 13)
```python
from app.main import app
```

### Added Limiter Access (Line 16)
```python
limiter = app.state.limiter
```

### Rate Limited Endpoints

#### 1. POST /videos/upload (Lines 31-32)
**Added Decorator:**
```python
@limiter.limit("5/minute")
```
**Location:** Before `def upload_video(...)`

#### 2. POST /videos/{video_id}/views (Lines 60-61)
**Added Decorator:**
```python
@limiter.limit("30/minute")
```
**Location:** Before `def increment_video_views(...)`

#### 3. DELETE /videos/{video_id} (Lines 67-68)
**Added Decorator:**
```python
@limiter.limit("10/minute")
```
**Location:** Before `def delete_video(...)`

#### 4. POST /videos/{video_id}/comments (Lines 109-110)
**Added Decorator:**
```python
@limiter.limit("20/minute")
```
**Location:** Before `def post_comment(...)`

---

## File 3: app/api/routes/users.py

### Added Imports (Line 14)
```python
from app.main import app
```

### Added Limiter Access (Line 17)
```python
limiter = app.state.limiter
```

### Rate Limited Endpoints

#### 1. POST /users (Lines 32-33)
**Added Decorator:**
```python
@limiter.limit("10/minute")
```
**Location:** Before `def create_user(...)`

#### 2. POST /users/{user_id}/subscriptions/{creator_id} (Lines 70-71)
**Added Decorator:**
```python
@limiter.limit("30/minute")
```
**Location:** Before `def subscribe(...)`

#### 3. DELETE /users/{user_id}/subscriptions/{creator_id} (Lines 80-81)
**Added Decorator:**
```python
@limiter.limit("30/minute")
```
**Location:** Before `def unsubscribe(...)`

---

## Summary of Additions

### Total Changes:
- **Files Modified:** 3
- **New Imports:** 2 (1x from slowapi, 1x from app.main in route files)
- **New Functions:** 1 (get_limiter in dependencies.py)
- **Limiter Initializations:** 2 (in videos.py and users.py)
- **Rate Limit Decorators Added:** 7
- **Lines Added:** ~20 (including imports, limiter access, and decorators)

### Decorator Breakdown:
- 5/minute: 1 endpoint (video upload)
- 10/minute: 2 endpoints (user creation, video deletion)
- 20/minute: 1 endpoint (comments)
- 30/minute: 3 endpoints (video views, subscribe, unsubscribe)

All changes maintain backward compatibility and don't modify existing function signatures or behavior.
