"""
End-to-end test script for the RAG system.
Tests document loading and question answering without the HTTP API.
"""

import asyncio
import logging
import os

from app.core.config import get_settings
from app.services.rag_service import RAGService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


def create_sample_document() -> None:
    """Create a sample Thai-language college info document for testing."""
    sample_text = """
    Sample Technical College Information

    Student Admissions:
    The college accepts new students during March-May each year.
    You can apply online at the college website or in person at the administration building.

    Programs Offered:
    1. Information Technology (IT)
    2. Computer Technology
    3. Automotive
    4. Electrical Engineering
    5. Accounting

    Tuition:
    - Registration per semester: 3,500 THB
    - Accident insurance: 500 THB/year
    - Student uniform: 2,000 THB

    Scholarships:
    The college offers scholarships for students with good academic records
    or students who lack financial resources.
    Apply at the Student Affairs office.

    Hours:
    Monday-Friday: 08:00-16:30
    Saturday: 08:00-12:00
    Sunday and public holidays: Closed

    Contact:
    Phone: 02-XXX-XXXX
    Email: info@techcollege.ac.th
    Website: www.techcollege.ac.th
    """

    os.makedirs("./data/documents", exist_ok=True)

    with open("./data/documents/sample_college_info.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)

    print("Created sample document: sample_college_info.txt")


async def main() -> None:
    """Run the end-to-end test."""
    print("=" * 60)
    print("  College RAG System - E2E Test")
    print("=" * 60)
    print()

    # Create sample document
    print("Creating sample document...")
    create_sample_document()
    print()

    # Initialize RAG service
    settings = get_settings()
    rag = RAGService(settings)
    await rag.initialize()
    print()

    # Load document
    print("Loading document into the system...")
    result = await rag.load_document(
        "./data/documents/sample_college_info.txt",
        "sample_college_info.txt",
    )
    print(f"Result: {result}")
    print()

    # Stats
    print("System stats:")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # Test queries
    print("=" * 60)
    print("  Test Queries")
    print("=" * 60)
    print()

    test_questions = [
        "When does the college accept new students?",
        "What programs are offered?",
        "How much is tuition?",
        "What days is the college open?",
        "Are there scholarships available?",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n[Question {i}]")
        print(f"Q: {question}")
        print("-" * 60)

        result = await rag.query(question)

        print(f"A: {result['answer']}")
        if result["sources"]:
            print(f"Sources: {', '.join(result['sources'])}")
        print()

    # Shutdown
    await rag.shutdown()

    print("=" * 60)
    print("  Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
