from backend.main import app

# Minimal wrapper so `uvicorn main:app --reload` works from repository root.
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
