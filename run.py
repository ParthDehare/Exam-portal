"""
MockExam Pro - Startup Script
Run: python run.py
"""
import asyncio
import subprocess
import sys

async def setup():
    from seed import seed
    await seed()

if __name__ == "__main__":
    print("=" * 50)
    print("  MockExam Pro - Starting Up")
    print("=" * 50)

    asyncio.run(setup())

    print("\n[OK] Server starting at http://localhost:8000")
    print("     Docs:      http://localhost:8000/docs")
    print("     Admin:     admin@mockexam.com / Admin@123")
    print("     Candidate: john@example.com  / Test@123")
    print("=" * 50 + "\n")

    subprocess.run([
        sys.executable, "-m", "uvicorn", "main:app",
        "--reload", "--host", "127.0.0.1", "--port", "8000"
    ])
