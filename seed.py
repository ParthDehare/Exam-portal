import asyncio
from sqlalchemy import select
from app.database.db import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.models.assessment import Assessment
from app.models.question import Question, QuestionType
from app.services.auth import hash_password

async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Skip if already seeded
        existing = await db.execute(select(User))
        if existing.scalars().first():
            print("[INFO] Database already seeded. Skipping.")
            return

        # Users
        admin = User(fullname="Admin User", email="admin@mockexam.com",
                     password=hash_password("Admin@123"), role=UserRole.admin)
        candidate = User(fullname="John Doe", email="john@example.com",
                         password=hash_password("Test@123"), role=UserRole.candidate)
        db.add_all([admin, candidate])
        await db.commit()

        # Assessments
        a1 = Assessment(title="Python Fundamentals", description="Test your Python basics",
                        duration=30, total_marks=10, passing_marks=6, difficulty="easy", category="Programming")
        a2 = Assessment(title="Data Structures & Algorithms", description="DSA concepts assessment",
                        duration=60, total_marks=20, passing_marks=12, difficulty="hard", category="Computer Science")
        a3 = Assessment(title="Web Development Basics", description="HTML, CSS, JS fundamentals",
                        duration=45, total_marks=15, passing_marks=9, difficulty="medium", category="Web")
        db.add_all([a1, a2, a3])
        await db.commit()

        questions = [
            Question(assessment_id=a1.id, question_text="What is the output of print(type([]))?",
                     option_a="<class 'list'>", option_b="<class 'tuple'>", option_c="<class 'dict'>", option_d="<class 'set'>",
                     correct_answer="A", marks=1, topic="Data Types", explanation="[] creates an empty list"),
            Question(assessment_id=a1.id, question_text="Which keyword is used to define a function in Python?",
                     option_a="func", option_b="define", option_c="def", option_d="function",
                     correct_answer="C", marks=1, topic="Functions"),
            Question(assessment_id=a1.id, question_text="Python is case-sensitive.",
                     option_a="True", option_b="False", option_c=None, option_d=None,
                     correct_answer="True", marks=1, topic="Basics", question_type=QuestionType.true_false),
            Question(assessment_id=a1.id, question_text="What does len() function return?",
                     option_a="Sum of elements", option_b="Number of elements", option_c="Last element", option_d="First element",
                     correct_answer="B", marks=1, topic="Built-in Functions"),
            Question(assessment_id=a1.id, question_text="Which of the following is a mutable data type?",
                     option_a="tuple", option_b="string", option_c="list", option_d="int",
                     correct_answer="C", marks=1, topic="Data Types"),
            Question(assessment_id=a1.id, question_text="What is the correct way to create a dictionary?",
                     option_a="d = []", option_b="d = ()", option_c="d = {}", option_d="d = <>",
                     correct_answer="C", marks=1, topic="Data Types"),
            Question(assessment_id=a1.id, question_text="Which operator is used for floor division?",
                     option_a="/", option_b="//", option_c="%", option_d="**",
                     correct_answer="B", marks=1, topic="Operators"),
            Question(assessment_id=a1.id, question_text="What is the output of 2**3?",
                     option_a="6", option_b="8", option_c="9", option_d="5",
                     correct_answer="B", marks=1, topic="Operators"),
            Question(assessment_id=a1.id, question_text="How do you start a comment in Python?",
                     option_a="//", option_b="/*", option_c="#", option_d="--",
                     correct_answer="C", marks=1, topic="Syntax"),
            Question(assessment_id=a1.id, question_text="Which method adds an element to the end of a list?",
                     option_a="add()", option_b="insert()", option_c="push()", option_d="append()",
                     correct_answer="D", marks=1, topic="Lists"),

            Question(assessment_id=a2.id, question_text="What is the time complexity of binary search?",
                     option_a="O(n)", option_b="O(n^2)", option_c="O(log n)", option_d="O(1)",
                     correct_answer="C", marks=2, topic="Searching"),
            Question(assessment_id=a2.id, question_text="Which data structure uses LIFO principle?",
                     option_a="Queue", option_b="Stack", option_c="Tree", option_d="Graph",
                     correct_answer="B", marks=2, topic="Data Structures"),
            Question(assessment_id=a2.id, question_text="What is the worst case time complexity of QuickSort?",
                     option_a="O(n log n)", option_b="O(n)", option_c="O(n^2)", option_d="O(log n)",
                     correct_answer="C", marks=2, topic="Sorting"),
            Question(assessment_id=a2.id, question_text="Which traversal visits root first?",
                     option_a="Inorder", option_b="Postorder", option_c="Preorder", option_d="Level order",
                     correct_answer="C", marks=2, topic="Trees"),
            Question(assessment_id=a2.id, question_text="A linked list node contains data and a pointer to the next node.",
                     option_a="True", option_b="False", option_c=None, option_d=None,
                     correct_answer="True", marks=2, topic="Linked Lists", question_type=QuestionType.true_false),

            Question(assessment_id=a3.id, question_text="What does HTML stand for?",
                     option_a="Hyper Text Markup Language", option_b="High Tech Modern Language",
                     option_c="Hyper Transfer Markup Language", option_d="Home Tool Markup Language",
                     correct_answer="A", marks=1, topic="HTML"),
            Question(assessment_id=a3.id, question_text="Which CSS property controls text size?",
                     option_a="text-size", option_b="font-size", option_c="text-style", option_d="font-style",
                     correct_answer="B", marks=1, topic="CSS"),
            Question(assessment_id=a3.id, question_text="JavaScript is a server-side language only.",
                     option_a="True", option_b="False", option_c=None, option_d=None,
                     correct_answer="False", marks=1, topic="JavaScript", question_type=QuestionType.true_false),
        ]
        db.add_all(questions)
        await db.commit()
        print("[OK] Seed data created successfully!")
        print("     Admin:     admin@mockexam.com / Admin@123")
        print("     Candidate: john@example.com  / Test@123")

if __name__ == "__main__":
    asyncio.run(seed())
